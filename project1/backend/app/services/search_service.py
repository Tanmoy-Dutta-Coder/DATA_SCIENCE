import asyncio
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from ..models.schemas import (
    RepositoryResult,
    FileMatch,
    SearchResponse,
    RateLimitDetail,
    AgentConfig
)
from .config_service import config_service
from .github_client import github_client
from .cache_service import cache_service

class SearchService:
    def _hash_token(self, token: Optional[str]) -> str:
        if not token:
            return "anon"
        return hashlib.sha256(token.encode()).hexdigest()[:10]

    def _clean_query(self, query: str) -> str:
        # Strip dangerous or excessively long modifiers
        cleaned = " ".join(query.strip().split())
        return cleaned[:150]

    def _build_code_query_tier1(self, agent: AgentConfig, user_keywords: str) -> str:
        # Tier 1: Match primary file pattern + user keywords
        parts = []
        if agent.file_patterns:
            parts.append(f"filename:{agent.file_patterns[0]}")
        if user_keywords:
            parts.append(user_keywords)
        return " ".join(parts)

    def _build_code_query_tier2(self, agent: AgentConfig, user_keywords: str) -> str:
        # Tier 2: Broader filename match with multiple patterns
        if len(agent.file_patterns) > 1:
            filenames = " OR ".join([f"filename:{fn}" for fn in agent.file_patterns[:3]])
            parts = [f"({filenames})"]
        elif agent.file_patterns:
            parts = [f"filename:{agent.file_patterns[0]}"]
        else:
            parts = []
        if user_keywords:
            parts.append(user_keywords)
        return " ".join(parts)

    def _build_repo_query(self, agent: AgentConfig, user_keywords: str) -> str:
        # Tier 3: Search repos by topics or agent keywords
        if agent.repo_topics:
            topic_clause = " ".join([f"topic:{t}" for t in agent.repo_topics[:2]])
            if user_keywords:
                return f"{topic_clause} {user_keywords}"
            return topic_clause
        return f"{agent.display_name} {user_keywords}".strip()

    def _calculate_score(self, repo: RepositoryResult, has_file_match: bool) -> float:
        score = 0.0
        if has_file_match:
            score += 50.0
        # Stargazer boost up to 30
        score += min(repo.stargazers_count / 50.0, 30.0)
        # Fork boost up to 10
        score += min(repo.forks_count / 20.0, 10.0)
        return round(score, 2)

    def _normalize_code_items(self, items: List[Dict[str, Any]]) -> List[RepositoryResult]:
        repos_map: Dict[int, RepositoryResult] = {}

        for item in items:
            repo_data = item.get("repository", {})
            repo_id = repo_data.get("id")
            if not repo_id:
                continue

            # Build file match
            file_path = item.get("path", "")
            file_name = item.get("name", "")
            html_url = item.get("html_url", "")
            raw_url = html_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

            file_match = FileMatch(
                name=file_name,
                path=file_path,
                html_url=html_url,
                raw_url=raw_url
            )

            if repo_id not in repos_map:
                owner_data = repo_data.get("owner", {})
                repos_map[repo_id] = RepositoryResult(
                    id=repo_id,
                    name=repo_data.get("name", ""),
                    full_name=repo_data.get("full_name", ""),
                    owner_name=owner_data.get("login", ""),
                    owner_avatar_url=owner_data.get("avatar_url"),
                    html_url=repo_data.get("html_url", ""),
                    description=repo_data.get("description"),
                    stargazers_count=repo_data.get("stargazers_count", 0),
                    forks_count=repo_data.get("forks_count", 0),
                    open_issues_count=repo_data.get("open_issues_count", 0),
                    language=repo_data.get("language"),
                    topics=repo_data.get("topics", []),
                    updated_at=repo_data.get("updated_at", ""),
                    matched_files=[file_match],
                    match_source="code",
                    score=0.0
                )
            else:
                # Add file match to existing repo
                if not any(f.path == file_path for f in repos_map[repo_id].matched_files):
                    repos_map[repo_id].matched_files.append(file_match)

        results = list(repos_map.values())
        for r in results:
            r.score = self._calculate_score(r, has_file_match=True)
        return results

    def _normalize_repo_items(self, items: List[Dict[str, Any]]) -> List[RepositoryResult]:
        results = []
        for r in items:
            owner_data = r.get("owner", {})
            license_data = r.get("license") or {}
            repo_res = RepositoryResult(
                id=r.get("id", 0),
                name=r.get("name", ""),
                full_name=r.get("full_name", ""),
                owner_name=owner_data.get("login", ""),
                owner_avatar_url=owner_data.get("avatar_url"),
                html_url=r.get("html_url", ""),
                description=r.get("description"),
                stargazers_count=r.get("stargazers_count", 0),
                forks_count=r.get("forks_count", 0),
                open_issues_count=r.get("open_issues_count", 0),
                language=r.get("language"),
                topics=r.get("topics", []),
                updated_at=r.get("updated_at", ""),
                license_name=license_data.get("spdx_id") or license_data.get("name"),
                matched_files=[],
                match_source="repo",
                score=0.0
            )
            repo_res.score = self._calculate_score(repo_res, has_file_match=False)
            results.append(repo_res)
        return results

    async def search(
        self,
        agent_id: str,
        query: str,
        page: int = 1,
        per_page: int = 20,
        token: Optional[str] = None
    ) -> SearchResponse:
        agent = config_service.get_agent(agent_id)
        if not agent:
            available = ", ".join(config_service.get_all_agent_ids())
            raise ValueError(f"Unknown agent: '{agent_id}'. Supported agents: {available}")

        cleaned_kw = self._clean_query(query)
        cache_key = f"search:{agent_id}:{cleaned_kw}:{page}:{per_page}:{self._hash_token(token)}"
        
        cached_res = cache_service.get(cache_key)
        if cached_res:
            cached_res.cached = True
            return cached_res

        tier_used = "tier1_code"
        last_rate_limit: Optional[RateLimitDetail] = None
        results: List[RepositoryResult] = []
        total_count = 0

        # Tier 1: Exact Code Search
        tier1_query = self._build_code_query_tier1(agent, cleaned_kw)
        try:
            code_res, last_rate_limit = await github_client.search_code(
                query=tier1_query, page=page, per_page=per_page, token=token
            )
            items = code_res.get("items", [])
            total_count = code_res.get("total_count", 0)
            if items:
                results = self._normalize_code_items(items)
        except Exception:
            # On code search failure (e.g. unauthenticated limitation), proceed to fallback
            pass

        # Tier 2: Broader Code Search if Tier 1 was empty
        if not results:
            tier_used = "tier2_broad_code"
            tier2_query = self._build_code_query_tier2(agent, cleaned_kw)
            try:
                code_res, last_rate_limit = await github_client.search_code(
                    query=tier2_query, page=page, per_page=per_page, token=token
                )
                items = code_res.get("items", [])
                total_count = code_res.get("total_count", 0)
                if items:
                    results = self._normalize_code_items(items)
            except Exception:
                pass

        # Tier 3: Repository Search fallback
        if not results:
            tier_used = "tier3_repo_search"
            repo_query = self._build_repo_query(agent, cleaned_kw)
            try:
                repo_res, last_rate_limit = await github_client.search_repositories(
                    query=repo_query, page=page, per_page=per_page, token=token
                )
                items = repo_res.get("items", [])
                total_count = repo_res.get("total_count", 0)
                if items:
                    results = self._normalize_repo_items(items)
            except Exception as e:
                # If everything failed, re-raise error so user sees rate-limit or PAT message
                if not last_rate_limit:
                    raise e

        # Sort combined results by composite score descending
        results.sort(key=lambda x: x.score, reverse=True)

        # Generate helpful suggestions if 0 results
        suggestions = []
        if not results:
            default_samples = {
                "antigravity": ["pdf", "react testing", "sql", "automation", "api"],
                "claude": ["code review", "mcp", "playwright", "markdown", "git"],
                "codex": ["unit test", "copilot", "python docstring", "kubernetes"]
            }
            samples = agent.sample_queries or default_samples.get(agent.id, ["assistant", "tools", "testing"])
            suggestions = [s for s in samples if s != cleaned_kw][:4]

        response = SearchResponse(
            agent_id=agent.id,
            query=cleaned_kw,
            tier_used=tier_used,
            total_count=total_count,
            page=page,
            per_page=per_page,
            results=results,
            rate_limit=last_rate_limit,
            cached=False,
            suggestions=suggestions,
            install_path_hint=agent.install_path_hint
        )

        # Cache valid response for 30 mins
        cache_service.set(cache_key, response)
        return response

search_service = SearchService()
