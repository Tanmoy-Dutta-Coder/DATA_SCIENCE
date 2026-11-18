"""GitHub REST API crawler for the local SkillFinder SQLite catalog."""
import argparse
import asyncio
import base64
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from urllib.parse import quote

import httpx
from dotenv import dotenv_values, load_dotenv

from app.services.catalog_service import CatalogService, catalog_service
from app.services.config_service import config_service


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(ROOT_DIR / ".env")

TOPIC_QUERIES = ("claude-skills", "agent-skills", "codex", "antigravity")
CODE_QUERIES = ("filename:SKILL.md", "filename:AGENTS.md")
TOPIC_AGENT = {"claude-skills": "claude", "codex": "codex", "antigravity": "antigravity"}
AGENT_TERMS = {
    "claude": ("claude", "anthropic"),
    "codex": ("codex", "openai", "copilot"),
    "antigravity": ("antigravity", "gemini"),
}
CATEGORY_TERMS = {
    "development": ("code", "coding", "programming", "developer", "refactor", "git", "api"),
    "testing": ("test", "testing", "qa", "quality", "playwright", "pytest"),
    "data": ("data", "sql", "database", "analytics", "csv", "pandas"),
    "documents": ("document", "pdf", "word", "spreadsheet", "excel", "forms"),
    "research": ("research", "search", "sources", "citation", "literature"),
    "writing": ("writing", "copywriting", "blog", "content", "editorial"),
    "design": ("design", "figma", "ui", "ux", "visual", "image"),
    "devops": ("devops", "docker", "kubernetes", "deploy", "ci/cd", "cloud"),
    "security": ("security", "vulnerability", "owasp", "audit", "threat"),
    "automation": ("automation", "workflow", "browser", "scrape", "integration"),
}


def detect_agent(text: str, file_path: str = "", topic: Optional[str] = None) -> str:
    """Infer one supported agent from repository and skill-file evidence."""
    if topic in TOPIC_AGENT:
        return TOPIC_AGENT[topic]
    haystack = f"{text} {file_path}".lower()
    scores = {agent: sum(1 for term in terms if term in haystack) for agent, terms in AGENT_TERMS.items()}
    winner = max(scores, key=scores.get)
    if scores[winner] > 0:
        return winner
    if Path(file_path).name.lower() == "agents.md":
        return "codex"
    if Path(file_path).name.lower() == "skill.md":
        return "antigravity"
    return "general"


def detect_category(text: str) -> str:
    """Choose a concise category from common skill subject keywords."""
    haystack = text.lower()
    scores = {category: sum(1 for term in terms if term in haystack) for category, terms in CATEGORY_TERMS.items()}
    winner = max(scores, key=scores.get)
    return winner if scores[winner] else "general"


class GitHubCrawler:
    API_ROOT = "https://api.github.com"

    def __init__(self, token: Optional[str] = None, catalog: Optional[CatalogService] = None,
                 max_retries: int = 8, request_delay: float = 0.15):
        from_env_files = (dotenv_values(Path(__file__).resolve().parent / ".env").get("GITHUB_TOKEN")
                          or dotenv_values(ROOT_DIR / ".env").get("GITHUB_TOKEN") or "")
        self.token = (token if token is not None else (os.getenv("GITHUB_TOKEN") or from_env_files)).strip()
        self.catalog = catalog or catalog_service
        self.max_retries = max_retries
        self.request_delay = max(0.0, request_delay)
        self._repo_cache: Dict[str, Dict[str, Any]] = {}
        self._topic_agents: Dict[str, str] = {}
        self._topic_scanned: set[str] = set()
        self._topic_seen: Dict[str, set[str]] = {}

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "SkillFinder-Crawler/1.0"}
        if self.token:
            value = self.token
            if not value.startswith(("Bearer ", "token ")):
                value = f"Bearer {value}"
            headers["Authorization"] = value
        return headers

    @staticmethod
    def _retry_delay(response: Optional[httpx.Response], attempt: int) -> float:
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    return max(1.0, float(retry_after))
                except ValueError:
                    try:
                        return max(1.0, (parsedate_to_datetime(retry_after) - datetime.now(timezone.utc)).total_seconds())
                    except (TypeError, ValueError):
                        pass
            remaining = response.headers.get("X-RateLimit-Remaining")
            reset = response.headers.get("X-RateLimit-Reset")
            if remaining == "0" and reset:
                try:
                    return max(1.0, float(reset) - time.time() + 1)
                except ValueError:
                    pass
        return min(300.0, 2.0 ** attempt)

    async def _get(self, client: httpx.AsyncClient, url: str,
                   params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        last_error = None
        for attempt in range(self.max_retries + 1):
            delay_floor = max(self.request_delay, 2.1 if "/search/" in url else 0.0)
            if delay_floor:
                await asyncio.sleep(delay_floor)
            response = None
            try:
                response = await client.get(url, params=params)
                if response.status_code in (403, 429) or response.status_code >= 500:
                    if attempt >= self.max_retries:
                        response.raise_for_status()
                    delay = self._retry_delay(response, attempt)
                    print(f"GitHub returned {response.status_code}; retrying in {delay:.0f}s (attempt {attempt + 1}/{self.max_retries}).")
                    await asyncio.sleep(delay)
                    continue
                response.raise_for_status()
                return response
            except httpx.RequestError as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    raise RuntimeError(f"GitHub request failed after retries: {exc}") from exc
                delay = self._retry_delay(response, attempt)
                print(f"GitHub network error; retrying in {delay:.0f}s (attempt {attempt + 1}/{self.max_retries}).")
                await asyncio.sleep(delay)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in (403, 429) and exc.response.status_code < 500:
                    raise RuntimeError(f"GitHub API returned {exc.response.status_code}: {exc.response.text[:300]}") from exc
                last_error = exc
        raise RuntimeError(f"GitHub request failed after retries: {last_error}")

    async def _json(self, client: httpx.AsyncClient, url: str,
                    params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return (await self._get(client, url, params)).json()

    def _progress(self, run_id: str, source: str, query: str):
        with self.catalog.connect() as db:
            row = db.execute("SELECT next_page,completed FROM crawler_progress WHERE run_id=? AND source=? AND query=?",
                             (run_id, source, query)).fetchone()
        return (row["next_page"], bool(row["completed"])) if row else (1, False)

    def _save_progress(self, run_id: str, source: str, query: str, next_page: int, completed: bool):
        now = datetime.now(timezone.utc).isoformat()
        with self.catalog.connect() as db:
            db.execute("""INSERT INTO crawler_progress(run_id,source,query,next_page,completed,updated_at)
                VALUES(?,?,?,?,?,?) ON CONFLICT(run_id,source,query) DO UPDATE SET
                next_page=excluded.next_page,completed=excluded.completed,updated_at=excluded.updated_at""",
                (run_id, source, query, next_page, int(completed), now))

    async def _repo_details(self, client: httpx.AsyncClient, repo: Dict[str, Any]) -> Dict[str, Any]:
        full_name = repo.get("full_name", "")
        if full_name not in self._repo_cache:
            details = await self._json(client, f"{self.API_ROOT}/repos/{full_name}")
            self._repo_cache[full_name] = details
        return self._repo_cache[full_name]

    async def _file_text(self, client: httpx.AsyncClient, item: Dict[str, Any]) -> str:
        content_url = item.get("url")
        if not content_url:
            return ""
        payload = await self._json(client, content_url)
        content = payload.get("content", "")
        if content and payload.get("encoding") == "base64":
            try:
                return base64.b64decode(content).decode("utf-8", errors="replace")[:200_000]
            except (ValueError, TypeError):
                return ""
        download_url = payload.get("download_url")
        if download_url:
            response = await self._get(client, download_url)
            return response.text[:200_000]
        return ""

    async def _crawl_topic_repo(self, client: httpx.AsyncClient, item: Dict[str, Any], topic: str,
                                files_per_repo: int = 5):
        """Use topic results as repository seeds, then index matching skill files from each tree."""
        repo = await self._repo_details(client, item)
        full_name = repo.get("full_name", "")
        if not full_name or full_name in self._topic_scanned:
            return
        self._topic_scanned.add(full_name)
        if topic in TOPIC_AGENT:
            self._topic_agents[full_name] = TOPIC_AGENT[topic]
        branch = repo.get("default_branch")
        if not branch:
            return
        tree = await self._json(client, f"{self.API_ROOT}/repos/{full_name}/git/trees/{quote(branch, safe='')}",
                                {"recursive": 1})
        matching = [entry for entry in tree.get("tree", [])
                    if entry.get("type") == "blob" and Path(entry.get("path", "")).name.lower() in {"skill.md", "agents.md"}]
        for entry in matching[:files_per_repo]:
            path = entry["path"]
            url = f"{self.API_ROOT}/repos/{full_name}/contents/{quote(path, safe='/')}"
            payload = await self._json(client, url, {"ref": branch})
            skill_text = self._decode_file(payload)
            await self._upsert(repo, path, skill_text, topic=topic,
                               agent_hint=self._topic_agents.get(full_name))

    @staticmethod
    def _decode_file(payload: Dict[str, Any]) -> str:
        content = payload.get("content", "")
        if content and payload.get("encoding") == "base64":
            try:
                return base64.b64decode(content).decode("utf-8", errors="replace")[:200_000]
            except (ValueError, TypeError):
                return ""
        return ""

    async def _search_pages(self, client: httpx.AsyncClient, run_id: str, source: str,
                            query: str, max_pages: int, topic: Optional[str] = None,
                            topic_repos: int = 50) -> int:
        page, complete = self._progress(run_id, source, query)
        if complete:
            return 0
        processed = 0
        endpoint = "search/repositories" if source == "topic" else "search/code"
        while page <= max_pages:
            print(f"[{source}] {query} page {page}/{max_pages}")
            payload = await self._json(client, f"{self.API_ROOT}/{endpoint}",
                                      {"q": query, "per_page": 100, "page": page})
            items = payload.get("items", [])
            for item in items:
                if source == "topic":
                    full_name = item.get("full_name")
                    seen = self._topic_seen.setdefault(topic or "", set())
                    if full_name and full_name not in seen and len(seen) < topic_repos:
                        seen.add(full_name)
                        if full_name not in self._topic_scanned:
                            await self._crawl_topic_repo(client, item, topic or "")
                else:
                    repo = item.get("repository") or {}
                    if not repo.get("full_name"):
                        continue
                    details = await self._repo_details(client, repo)
                    skill_text = await self._file_text(client, item)
                    await self._upsert(details, item.get("path", ""), skill_text,
                                       agent_hint=self._topic_agents.get(details.get("full_name", "")))
                processed += 1
            page += 1
            done = len(items) < 100 or (source == "topic" and len(self._topic_seen.get(topic or "", set())) >= topic_repos)
            self._save_progress(run_id, source, query, page, done)
            if done or page > max_pages:
                break
        return processed

    async def _upsert(self, repo: Dict[str, Any], path: str = "", skill_text: str = "",
                      topic: Optional[str] = None, agent_hint: Optional[str] = None):
        full_name = repo.get("full_name")
        if not full_name:
            return
        topics = repo.get("topics", []) or []
        description = repo.get("description") or ""
        text_for_detection = f"{full_name} {description} {' '.join(topics)} {skill_text}"
        agent = agent_hint or detect_agent(text_for_detection, path, topic)
        combined_text = f"{text_for_detection} {path}"
        category = detect_category(combined_text)
        name = Path(path).stem if path else repo.get("name", full_name.split("/")[-1])
        if name.lower() in ("skill", "agents") or not name:
            name = repo.get("name", full_name.split("/")[-1])
        owner_data = repo.get("owner") or {}
        license_data = repo.get("license") or {}
        license_name = license_data.get("spdx_id") or license_data.get("name")
        html_url = f"https://github.com/{full_name}"
        install_path = ""
        agent_config = config_service.get_agent(agent)
        if agent_config:
            install_path = agent_config.install_path_hint
        with self.catalog.connect() as db:
            db.execute("""INSERT INTO skills(name,description,repo,owner,agent,category,tags,skill_file_path,
                skill_text,stars,forks,last_updated,archived,license,install_path)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(repo,agent,skill_file_path) DO UPDATE SET
                name=excluded.name,description=excluded.description,owner=excluded.owner,category=excluded.category,
                tags=excluded.tags,skill_text=excluded.skill_text,stars=excluded.stars,forks=excluded.forks,
                last_updated=excluded.last_updated,archived=excluded.archived,license=excluded.license,
                install_path=excluded.install_path""",
                (name, description, full_name, owner_data.get("login", full_name.split("/")[0]), agent,
                 category, json.dumps(topics), path, skill_text or description,
                 repo.get("stargazers_count", 0), repo.get("forks_count", 0), repo.get("updated_at"),
                 int(bool(repo.get("archived", False))), license_name, install_path))

    async def run(self, max_pages: int = 10, run_id: Optional[str] = None, fresh: bool = False,
                  topic_repos: int = 50) -> Dict[str, Any]:
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN is missing. Add it to backend/.env or the project .env file.")
        run_id = run_id or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if fresh:
            with self.catalog.connect() as db:
                db.execute("DELETE FROM crawler_progress WHERE run_id=?", (run_id,))
        self._repo_cache.clear()
        self._topic_agents.clear()
        self._topic_scanned.clear()
        self._topic_seen.clear()
        self.catalog._set_meta("crawl_status", "running")
        self.catalog._set_meta("crawl_error", "")
        started_at = datetime.now(timezone.utc).isoformat()
        topic_count = code_count = 0
        try:
            async with httpx.AsyncClient(timeout=30, headers=self._headers()) as client:
                for topic in TOPIC_QUERIES:
                    topic_count += await self._search_pages(client, run_id, "topic", f"topic:{topic}", max_pages, topic, topic_repos)
                for query in CODE_QUERIES:
                    code_count += await self._search_pages(client, run_id, "code", query, max_pages)
            with self.catalog.connect() as db:
                self.catalog._rebuild_fts(db)
                db.execute("INSERT INTO catalog_meta(key,value) VALUES('last_crawl',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                           (datetime.now(timezone.utc).isoformat(),))
            self.catalog._set_meta("crawl_status", "completed")
            self.catalog._set_meta("crawl_error", "")
            with self.catalog.connect() as db:
                skill_count = db.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
            return {"run_id": run_id, "topic_results": topic_count, "code_results": code_count,
                    "skills_in_catalog": skill_count, "started_at": started_at}
        except Exception as exc:
            self.catalog._set_meta("crawl_status", "failed")
            self.catalog._set_meta("crawl_error", str(exc)[:500])
            raise


github_crawler = GitHubCrawler()


def seconds_until(utc_hhmm: str) -> float:
    hour, minute = (int(part) for part in utc_hhmm.split(":"))
    now = datetime.now(timezone.utc)
    run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if run_at <= now:
        run_at += timedelta(days=1)
    return (run_at - now).total_seconds()


async def schedule_nightly(crawler: GitHubCrawler, at_utc: str, max_pages: int, topic_repos: int):
    while True:
        delay = seconds_until(at_utc)
        print(f"Next catalog crawl in {delay / 3600:.1f} hours (UTC {at_utc}).")
        await asyncio.sleep(delay)
        try:
            print(json.dumps(await crawler.run(max_pages=max_pages, topic_repos=topic_repos), indent=2))
        except Exception as exc:
            print(f"Nightly crawl failed: {exc}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crawl GitHub skills into the local SQLite catalog.")
    parser.add_argument("command", nargs="?", choices=("run", "schedule"), default="run")
    parser.add_argument("--max-pages", type=int, default=10, help="Pages to resume/scan per query (up to 10).")
    parser.add_argument("--topic-repos", type=int, default=50, help="Topic-search repos to inspect per topic (up to 1000).")
    parser.add_argument("--run-id", help="Progress key; defaults to today's UTC date for resume support.")
    parser.add_argument("--fresh", action="store_true", help="Clear this run ID's checkpoints before crawling.")
    parser.add_argument("--at", default="02:00", help="Nightly schedule time in UTC (HH:MM).")
    return parser


def main(argv: Optional[Iterable[str]] = None):
    args = build_parser().parse_args(argv)
    if args.max_pages < 1 or args.max_pages > 10:
        raise SystemExit("--max-pages must be between 1 and 10.")
    if args.topic_repos < 1 or args.topic_repos > 1000:
        raise SystemExit("--topic-repos must be between 1 and 1000.")
    if not re.fullmatch(r"\d{2}:\d{2}", args.at):
        raise SystemExit("--at must use 24-hour UTC HH:MM format.")
    hour, minute = map(int, args.at.split(":"))
    if hour > 23 or minute > 59:
        raise SystemExit("--at must use 24-hour UTC HH:MM format.")
    crawler = GitHubCrawler()
    if args.command == "schedule":
        asyncio.run(schedule_nightly(crawler, args.at, args.max_pages, args.topic_repos))
    else:
        print(json.dumps(asyncio.run(crawler.run(args.max_pages, args.run_id, args.fresh, args.topic_repos)), indent=2))


if __name__ == "__main__":
    main()
