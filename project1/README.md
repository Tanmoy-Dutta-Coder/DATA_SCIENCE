# SkillFinder 🔍

**SkillFinder** is a web tool to discover AI agent skill definitions, custom instructions, and prompt templates across GitHub repositories for **Claude**, **OpenAI Codex & Copilot**, and **Google Antigravity**.

---

## Features
- **Targeted AI Agent Profiles**:
  - **Google Antigravity**: Discovers `SKILL.md`, `workflow.json`, and agent definitions inside `skills/` and `.gemini/antigravity/`.
  - **Anthropic Claude**: Discovers `CLAUDE.md`, `.claude/commands`, and Model Context Protocol (`mcp.json`) server configs.
  - **OpenAI Codex & Copilot**: Discovers `.copilot-instructions.md`, `codex.md`, and OpenAI assistant instruction files.
- **Hybrid Multi-Tier Search**:
  - **Tier 1 (Direct Code Search)**: Matches exact skill file signatures and target paths.
  - **Tier 2 (Broad Code Search)**: Broadens search across all repositories matching filename signatures.
  - **Tier 3 (Repository Search & Topics)**: Discovers repositories tagged with relevant topics (`topic:claude-skill`, `topic:antigravity-skill`, etc.) when code queries are sparse.
- **Smart Result Ranking & Deduplication**:
  - Scores repositories by verified skill file matches (+50 pts), GitHub stars, and fork activity.
  - Displays matched file paths with one-click direct links to GitHub raw content and web view.
- **Rate-Limit Resilience & In-Memory Caching**:
  - Responses cached with 30-minute TTL to stay within GitHub search quotas.
  - Optional user-supplied GitHub Personal Access Token (PAT) support stored securely in browser `localStorage`.
  - Live rate-limit monitoring pill in the header.

---

## Project Structure

```
skillfinder/
├── backend/
│   ├── app/
│   │   ├── config/
│   │   │   ├── agents.yaml      # Agent search rule definitions (YAML)
│   │   │   └── agents.json      # Agent search rule definitions (JSON)
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic v2 schemas
│   │   ├── services/
│   │   │   ├── config_service.py# Config parser & agent metadata
│   │   │   ├── github_client.py # Async GitHub REST API client
│   │   │   ├── search_service.py# Multi-tier query builder & scoring
│   │   │   └── cache_service.py # In-memory TTL caching
│   │   ├── api/
│   │   │   └── routes.py        # Endpoints: /api/agents, /api/search, /api/rate-limit
│   │   ├── config.py            # App settings & environment loader
│   │   └── main.py              # FastAPI app & CORS middleware
│   ├── tests/
│   │   └── test_backend.py      # Backend unit tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx           # Brand & quota monitor
│   │   │   ├── AgentSelector.tsx    # Antigravity / Claude / Codex cards
│   │   │   ├── SearchBar.tsx        # Search input with shortcut '/'
│   │   │   ├── FilterBar.tsx        # Sorting & tier badges
│   │   │   ├── ResultCard.tsx       # Repo card & matched skill file links
│   │   │   ├── EmptyState.tsx       # Suggestions & advice
│   │   │   └── TokenModal.tsx       # Personal access token setup
│   │   ├── services/
│   │   │   └── api.ts               # Frontend API client & PAT handling
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript interfaces
│   │   ├── App.tsx                  # Root state orchestration
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
└── README.md
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.15)
- Node.js 18+ and npm

### 2. Start the Backend (FastAPI)

```bash
cd backend

# Activate the virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# (Optional) Set your GitHub Personal Access Token in .env
copy .env.example .env
# Edit .env with your GITHUB_TOKEN=...

# Run the FastAPI server
$env:PYTHONPATH="."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be running at `http://127.0.0.1:8000`. You can inspect the interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

### 3. Start the Frontend (React + Vite)

```bash
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Vite dev server
npm run dev
```

Open `http://localhost:5173` in your browser.

