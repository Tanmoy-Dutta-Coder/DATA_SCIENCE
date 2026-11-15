import os
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import httpx
from dotenv import load_dotenv
from cachetools import TTLCache

# Load environment variables (.env in backend/ or root)
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")

# In-memory cache with a 10-minute (600 seconds) TTL
CACHE_TTL = 600
_search_cache: TTLCache = TTLCache(maxsize=500, ttl=CACHE_TTL)

# GitHub API Base URL
GITHUB_API_BASE = "https://api.github.com"


class GitHubRateLimitError(Exception):
    """Raised when GitHub API rate limits (403 or 429) are encountered."""
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class GitHubSearchError(Exception):
    """Raised for non-rate-limit GitHub search errors."""
    pass


def load_agents_config() -> Dict[str, Any]:
    """Reads the agent configuration from agents_config.json."""
    config_path = BASE_DIR / "agents_config.json"
    if not config_path.exists():
        # Fallback to app/config/agents.json if needed
        config_path = BASE_DIR / "app" / "config" / "agents.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Agent config file not found at {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Support both {"agents": {...}} and direct {...}
    return data.get("agents", data)


def _get_headers() -> Dict[str, str]:
    """Constructs request headers including optional authorization token."""
    token = os.getenv("GITHUB_TOKEN", "").strip()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "SkillFinder/1.0",
    }
    if token:
        auth_value = token if (token.startswith("Bearer ") or token.startswith("token ")) else f"Bearer {token}"
        headers["Authorization"] = auth_value
    return headers


def _extract_retry_after(response: httpx.Response) -> int:
    """Extracts wait time in seconds from Retry-After or x-ratelimit-reset headers."""
    retry_header = response.headers.get("Retry-After")
    if retry_header and retry_header.isdigit():
        return int(retry_header)

    reset_ts = response.headers.get("x-ratelimit-reset")
    if reset_ts and reset_ts.isdigit():
        remaining_seconds = int(reset_ts) - int(time.time())
        return max(remaining_seconds, 1)

    return 60


def _parse_timestamp(iso_str: Optional[str]) -> float:
    """Safely parses ISO timestamp to unix float for sorting."""
    if not iso_str:
        return 0.0
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.timestamp()
    except Exception:
        return 0.0


def _calculate_keyword_score(repo: Dict[str, Any], keywords: str) -> int:
    """
    Computes a keyword relevance match score:
    - 5 points per keyword found in repo name
    - 4 points per keyword found in topics
    - 3 points per keyword found in description
    - 10 bonus points if direct skill files were matched
    - 2 points per keyword found in matched file paths
    """
    if not keywords.strip():
        return 10 if repo.get("matched_files") else 0

    tokens = [k.lower() for k in keywords.strip().split() if len(k) > 1]
    if not tokens:
        return 0

    score = 0
    name_lower = (repo.get("name") or "").lower()
    desc_lower = (repo.get("description") or "").lower()
    topics = [t.lower() for t in repo.get("topics", [])]
    matched_files = repo.get("matched_files", [])

    if matched_files:
        score += 10

    for token in tokens:
        if token in name_lower:
            score += 5
        if any(token in t for t in topics):
            score += 4
        if token in desc_lower:
            score += 3
        for path in matched_files:
            if token in path.lower():
                score += 2

    return score


async def _search_repositories(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    agent_config: Dict[str, Any],
    keywords: str
) -> List[Dict[str, Any]]:
    """Performs /search/repositories using topic + keywords sorted by stars."""
    repo_topics = agent_config.get("repo_topics", [])
    query_parts = []

    if repo_topics:
        # Use primary topic(s)
        topic_clause = " ".join([f"topic:{t}" for t in repo_topics[:2]])
        query_parts.append(topic_clause)

    if keywords.strip():
        query_parts.append(keywords.strip())

    if not query_parts:
        return []

    q = " ".join(query_parts)
    params = {
        "q": q,
        "sort": "stars",
        "order": "desc",
        "per_page": 30
    }

    try:
        response = await client.get(
            f"{GITHUB_API_BASE}/search/repositories",
            headers=headers,
            params=params,
            timeout=15.0
        )
    except (httpx.RequestError, httpx.TimeoutException) as net_err:
        raise GitHubSearchError(f"Network error querying repositories: {str(net_err)}") from net_err

    if response.status_code in (403, 429):
        retry_secs = _extract_retry_after(response)
        raise GitHubRateLimitError(
            f"GitHub repository search rate limit exceeded. Retry after {retry_secs} seconds.",
            retry_after=retry_secs
        )

    if response.status_code == 422:
        # Invalid query syntax or empty result set
        return []

    if response.status_code != 200:
        raise GitHubSearchError(f"GitHub search/repositories returned status {response.status_code}: {response.text}")

    data = response.json()
    return data.get("items", [])


async def _search_code(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    agent_config: Dict[str, Any],
    keywords: str
) -> List[Dict[str, Any]]:
    """Performs /search/code using 'filename:<pattern> <keywords>'."""
    file_patterns = agent_config.get("file_patterns", [])
    if not file_patterns:
        return []

    # Use first 2 patterns to keep query within GitHub 256 character limit
    if len(file_patterns) > 1:
        pattern_clause = " OR ".join([f"filename:{p}" for p in file_patterns[:2]])
        q = f"({pattern_clause})"
    else:
        q = f"filename:{file_patterns[0]}"

    if keywords.strip():
        q += f" {keywords.strip()}"

    params = {
        "q": q,
        "per_page": 30
    }

    try:
        response = await client.get(
            f"{GITHUB_API_BASE}/search/code",
            headers=headers,
            params=params,
            timeout=15.0
        )
    except (httpx.RequestError, httpx.TimeoutException) as net_err:
        raise GitHubSearchError(f"Network error querying code search: {str(net_err)}") from net_err

    if response.status_code in (403, 429):
        retry_secs = _extract_retry_after(response)
        raise GitHubRateLimitError(
            f"GitHub code search rate limit exceeded. Retry after {retry_secs} seconds.",
            retry_after=retry_secs
        )

    if response.status_code == 422:
        return []

    # 401 = no auth token; code search silently skipped, repo search will cover it
    if response.status_code == 401:
        return []

    if response.status_code != 200:
        raise GitHubSearchError(f"GitHub search/code returned status {response.status_code}: {response.text}")

    data = response.json()
    return data.get("items", [])


async def search_skills(agent: str, keywords: str = "") -> List[Dict[str, Any]]:
    """
    Discovers AI agent skills on GitHub for a given agent and search keywords.

    1. Reads agent config from agents_config.json.
    2. Runs /search/repositories (topic + keywords, sorted by stars)
       and /search/code (filename:<pattern> + keywords).
    3. Merges and de-duplicates results by repository.
    4. Extracts: name, owner, description, stars, last_updated, html_url, matched_files.
    5. Ranks by keyword match, then stars, then recent activity.
    6. Caps output to max 30 results and caches response for 10 minutes.
    """
    agent_id = agent.lower().strip()
    clean_kw = keywords.strip()

    # 1. Check in-memory cache
    cache_key = (agent_id, clean_kw)
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    # 2. Read agent's config
    configs = load_agents_config()
    if agent_id not in configs:
        available = ", ".join(configs.keys())
        raise ValueError(f"Unknown agent '{agent}'. Available agents: {available}")

    agent_cfg = configs[agent_id]
    headers = _get_headers()

    # 3. Concurrently execute repository and code searches
    async with httpx.AsyncClient(timeout=20.0) as client:
        results_repo, results_code = await asyncio.gather(
            _search_repositories(client, headers, agent_cfg, clean_kw),
            _search_code(client, headers, agent_cfg, clean_kw),
            return_exceptions=True
        )

    # Inspect errors
    repo_items: List[Dict[str, Any]] = []
    code_items: List[Dict[str, Any]] = []

    # If both searches hit rate limits, propagate rate limit error
    if isinstance(results_repo, GitHubRateLimitError) and isinstance(results_code, GitHubRateLimitError):
        raise results_repo
    elif isinstance(results_repo, GitHubRateLimitError) and not isinstance(results_code, list):
        raise results_repo
    elif isinstance(results_code, GitHubRateLimitError) and not isinstance(results_repo, list):
        raise results_code

    if isinstance(results_repo, list):
        repo_items = results_repo

    if isinstance(results_code, list):
        code_items = results_code

    # If both returned empty and there was a fatal network error
    if not repo_items and not code_items:
        if isinstance(results_repo, GitHubSearchError):
            raise results_repo
        if isinstance(results_code, GitHubSearchError):
            raise results_code

    # 4. Merge and de-duplicate by repository (keyed by repo id or html_url)
    merged_repos: Dict[str, Dict[str, Any]] = {}

    # Ingest code search matches first (they contain verified matched skill file paths)
    for c_item in code_items:
        repo_obj = c_item.get("repository") or {}
        repo_url = repo_obj.get("html_url")
        if not repo_url:
            continue

        owner_info = repo_obj.get("owner") or {}
        file_path = c_item.get("path", "")

        if repo_url not in merged_repos:
            merged_repos[repo_url] = {
                "name": repo_obj.get("name", ""),
                "owner": owner_info.get("login", ""),
                "description": repo_obj.get("description") or "",
                "stars": repo_obj.get("stargazers_count", 0),
                "last_updated": repo_obj.get("updated_at") or "",
                "html_url": repo_url,
                "topics": repo_obj.get("topics", []),
                "matched_files": [file_path] if file_path else []
            }
        else:
            if file_path and file_path not in merged_repos[repo_url]["matched_files"]:
                merged_repos[repo_url]["matched_files"].append(file_path)

    # Ingest repository search matches
    for r_item in repo_items:
        repo_url = r_item.get("html_url")
        if not repo_url:
            continue

        owner_info = r_item.get("owner") or {}

        if repo_url not in merged_repos:
            merged_repos[repo_url] = {
                "name": r_item.get("name", ""),
                "owner": owner_info.get("login", ""),
                "description": r_item.get("description") or "",
                "stars": r_item.get("stargazers_count", 0),
                "last_updated": r_item.get("updated_at") or "",
                "html_url": repo_url,
                "topics": r_item.get("topics", []),
                "matched_files": []
            }
        else:
            # Update stars, last_updated, and description with full repo info if available
            merged_repos[repo_url]["stars"] = r_item.get("stargazers_count", merged_repos[repo_url]["stars"])
            if r_item.get("description"):
                merged_repos[repo_url]["description"] = r_item.get("description")
            if r_item.get("updated_at"):
                merged_repos[repo_url]["last_updated"] = r_item.get("updated_at")
            if r_item.get("topics"):
                merged_repos[repo_url]["topics"] = list(
                    set(merged_repos[repo_url].get("topics", []) + r_item.get("topics", []))
                )

    # 5. Rank by keyword match, then stars, then recent activity
    results_list = list(merged_repos.values())

    for item in results_list:
        item["_kw_score"] = _calculate_keyword_score(item, clean_kw)
        item["_updated_ts"] = _parse_timestamp(item.get("last_updated"))

    results_list.sort(
        key=lambda x: (x["_kw_score"], x["stars"], x["_updated_ts"]),
        reverse=True
    )

    # 6. Format final output (max 30 results)
    final_output: List[Dict[str, Any]] = []
    for item in results_list[:30]:
        final_output.append({
            "name": item["name"],
            "owner": item["owner"],
            "description": item["description"],
            "stars": item["stars"],
            "last_updated": item["last_updated"],
            "html_url": item["html_url"],
            "matched_files": item["matched_files"]
        })

    # 7. Store in 10-minute in-memory cache
    _search_cache[cache_key] = final_output
    return final_output


if __name__ == "__main__":
    import sys

    test_agent = sys.argv[1] if len(sys.argv) > 1 else "claude"
    test_keywords = sys.argv[2] if len(sys.argv) > 2 else "mcp"

    print(f"Testing search_skills(agent='{test_agent}', keywords='{test_keywords}')...")
    try:
        output = asyncio.run(search_skills(test_agent, test_keywords))
        print(f"Success! Found {len(output)} repositories:")
        for r in output[:5]:
            print(f"- {r['owner']}/{r['name']} ({r['stars']} stars) | Matched files: {r['matched_files']}")
    except GitHubRateLimitError as rle:
        print(f"Rate limited: {rle}. Retry-After: {rle.retry_after}s")
    except Exception as e:
        print(f"Search failed: {e}")

