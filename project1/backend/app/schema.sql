PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    repo TEXT NOT NULL,
    owner TEXT NOT NULL,
    agent TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    skill_file_path TEXT NOT NULL DEFAULT '',
    skill_text TEXT NOT NULL DEFAULT '',
    stars INTEGER NOT NULL DEFAULT 0,
    forks INTEGER NOT NULL DEFAULT 0,
    last_updated TEXT,
    archived INTEGER NOT NULL DEFAULT 0 CHECK (archived IN (0, 1)),
    license TEXT,
    install_path TEXT NOT NULL DEFAULT '',
    UNIQUE (repo, agent, skill_file_path)
);

CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
    name,
    description,
    tags,
    skill_text,
    tokenize = 'unicode61 remove_diacritics 2'
);

CREATE TABLE IF NOT EXISTS feedback (
    skill_id INTEGER NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('click', 'copy', 'open')),
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skills_agent_repo ON skills(agent, repo);
CREATE INDEX IF NOT EXISTS idx_feedback_skill ON feedback(skill_id);

CREATE TABLE IF NOT EXISTS catalog_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS crawler_progress (
    run_id TEXT NOT NULL,
    source TEXT NOT NULL,
    query TEXT NOT NULL,
    next_page INTEGER NOT NULL DEFAULT 1,
    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
    updated_at TEXT NOT NULL,
    PRIMARY KEY (run_id, source, query)
);
