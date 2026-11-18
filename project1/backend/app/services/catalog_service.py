"""SQLite skills catalog, FTS search, feedback, and GitHub ingestion."""
import json
import os
import sqlite3
from pathlib import Path
from typing import Optional

from .config_service import config_service
from .query_understanding import understand
from .search import search_catalog


class CatalogService:
    def __init__(self, db_path: Optional[Path] = None):
        default_path = Path(__file__).resolve().parents[2] / "skillfinder.db"
        self.db_path = Path(db_path or os.getenv("SKILLFINDER_DB_PATH", default_path))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def connect(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def init_db(self):
        schema_path = Path(__file__).resolve().parent.parent / "schema.sql"
        with self.connect() as db:
            self._archive_legacy_schema(db)
            db.executescript(schema_path.read_text(encoding="utf-8"))
            self._migrate_legacy_rows(db)
            self._rebuild_fts(db)

    @staticmethod
    def _table_exists(db, table: str) -> bool:
        return db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone() is not None

    def _archive_legacy_schema(self, db):
        """Rename the previous normalized schema before creating the requested flat schema."""
        if self._table_exists(db, "skills"):
            columns = {row[1] for row in db.execute("PRAGMA table_info(skills)")}
            if "skill_id" not in columns and not self._table_exists(db, "skills_legacy"):
                db.execute("ALTER TABLE skills RENAME TO skills_legacy")
        if self._table_exists(db, "feedback"):
            columns = {row[1] for row in db.execute("PRAGMA table_info(feedback)")}
            if "skill_id" not in columns and not self._table_exists(db, "feedback_legacy"):
                db.execute("ALTER TABLE feedback RENAME TO feedback_legacy")
        if self._table_exists(db, "catalog_fts"):
            db.execute("DROP TABLE catalog_fts")

    def _migrate_legacy_rows(self, db):
        if not self._table_exists(db, "skills_legacy") or not self._table_exists(db, "repositories"):
            return
        rows = db.execute("""SELECT s.id, s.agent_id, s.path, s.content, r.name, r.description,
                            r.full_name, r.owner, r.stars, r.forks, r.topics, r.updated_at
                            FROM skills_legacy s JOIN repositories r ON r.id=s.repo_id""").fetchall()
        for row in rows:
            agent = config_service.get_agent(row["agent_id"])
            try:
                tags = json.loads(row["topics"] or "[]")
            except (TypeError, json.JSONDecodeError):
                tags = []
            db.execute("""INSERT OR IGNORE INTO skills(
                skill_id,name,description,repo,owner,agent,category,tags,skill_file_path,skill_text,
                stars,forks,last_updated,archived,license,install_path
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (row["id"], row["name"], row["description"] or "", row["full_name"], row["owner"],
                 row["agent_id"], tags[0] if tags else row["agent_id"], json.dumps(tags), row["path"],
                 row["content"] or "", row["stars"] or 0, row["forks"] or 0, row["updated_at"], 0,
                 None, agent.install_path_hint if agent else ""))

    @staticmethod
    def _rebuild_fts(db):
        db.execute("DELETE FROM skills_fts")
        db.execute("""INSERT INTO skills_fts(rowid,name,description,tags,skill_text)
                      SELECT skill_id,name,description,tags,skill_text FROM skills""")

    def search(self, agent: Optional[str], query: str, page: int = 1, per_page: int = 20,
               category: Optional[str] = None, min_stars: Optional[int] = None,
               updated: Optional[str] = None, sort: str = "relevance"):
        parsed = understand(query)
        core = parsed["core"]
        if not core:
            raise ValueError("Enter at least one search term.")
        terms = core.split()
        with self.connect() as db:
            search_results = search_catalog(db, parsed, agent, page, per_page, category, min_stars, updated, sort)
            samples = config_service.get_agent(agent) if agent else None
            suggestions = (samples.sample_queries if samples else []) if not search_results["results"] else []
            return {"agent": agent or "all", "keywords": terms, "query": parsed, **search_results,
                    "page": page, "per_page": min(per_page, 20),
                    "suggestions": suggestions, "catalog_updated_at": self.meta(db, "last_crawl")}

    def suggest(self, query: str, limit: int = 10):
        query = " ".join(query.lower().split())[:100]
        if not query:
            return []
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        name_pattern = escaped + "%"
        tag_pattern = "%" + escaped + "%"
        with self.connect() as db:
            rows = db.execute("""SELECT name,tags,repo FROM skills
                WHERE lower(name) LIKE ? ESCAPE '\\' OR lower(tags) LIKE ? ESCAPE '\\'
                LIMIT 1000""", (name_pattern, tag_pattern)).fetchall()
        repositories = {}
        for row in rows:
            name = (row["name"] or "").strip()
            if name.lower().startswith(query):
                repositories.setdefault((name, "skill_name"), set()).add(row["repo"])
            try:
                tags = json.loads(row["tags"] or "[]")
            except (TypeError, json.JSONDecodeError):
                tags = []
            for tag in tags:
                if isinstance(tag, str) and tag.lower().startswith(query):
                    repositories.setdefault((tag, "tag"), set()).add(row["repo"])
        suggestions = [{"text": value, "type": kind, "count": len(repos)}
                       for (value, kind), repos in repositories.items()]
        suggestions.sort(key=lambda item: (0 if item["type"] == "skill_name" else 1,
                                           -item["count"], item["text"].lower()))
        return suggestions[:max(1, min(limit, 20))]

    @staticmethod
    def meta(db, key):
        row = db.execute("SELECT value FROM catalog_meta WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    def _set_meta(self, key: str, value: str):
        with self.connect() as db:
            db.execute("INSERT INTO catalog_meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    def add_feedback(self, skill_id: int, query: str, action: str):
        with self.connect() as db:
            db.execute("INSERT INTO feedback(skill_id,query,action) VALUES(?,?,?)", (skill_id, query[:200], action))


catalog_service = CatalogService()
