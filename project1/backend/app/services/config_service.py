import json
from pathlib import Path
from typing import Dict, List, Optional
from ..models.schemas import AgentConfig, AgentSummary

class ConfigService:
    def __init__(self):
        # Look for agents_config.json in backend/ or app/config/
        self.backend_dir = Path(__file__).resolve().parent.parent.parent
        self.primary_config_path = self.backend_dir / "agents_config.json"
        self.fallback_config_path = Path(__file__).resolve().parent.parent / "config" / "agents.json"
        self._agents: Dict[str, AgentConfig] = {}
        self.load_config()

    def load_config(self) -> None:
        """Loads agent configuration dynamically from agents_config.json."""
        target_path = None
        if self.primary_config_path.exists():
            target_path = self.primary_config_path
        elif self.fallback_config_path.exists():
            target_path = self.fallback_config_path

        if not target_path:
            raise FileNotFoundError(
                f"Agent configuration file not found at {self.primary_config_path} or {self.fallback_config_path}"
            )

        with open(target_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Support both {"agents": { "claude": {...} }} and direct {"claude": {...}}
        agents_dict = raw_data.get("agents", raw_data)

        # Known color & icon themes for standard agents; new agents get sensible defaults
        theme_defaults = {
            "antigravity": {"badge_color": "emerald", "icon": "Sparkles", "desc": "Antigravity skills, workflows, and rules"},
            "claude": {"badge_color": "amber", "icon": "Bot", "desc": "Claude custom instructions and MCP servers"},
            "codex": {"badge_color": "blue", "icon": "Code2", "desc": "GitHub Copilot instructions and Codex prompts"},
        }

        self._agents = {}
        for agent_key, data in agents_dict.items():
            agent_id = agent_key.lower().strip()
            theme = theme_defaults.get(agent_id, {
                "badge_color": "indigo",
                "icon": "Cpu",
                "desc": f"{data.get('display_name', agent_id)} instructions and skills"
            })

            # Support file_patterns / code_search.filenames
            file_patterns = data.get("file_patterns") or data.get("code_search", {}).get("filenames", [])
            # Support repo_topics / repo_search.topics
            repo_topics = data.get("repo_topics") or data.get("repo_search", {}).get("topics", [])

            self._agents[agent_id] = AgentConfig(
                id=agent_id,
                display_name=data.get("display_name") or data.get("name") or agent_id.capitalize(),
                file_patterns=file_patterns,
                repo_topics=repo_topics,
                install_path_hint=data.get("install_path_hint", ""),
                description=data.get("description", theme["desc"]),
                badge_color=data.get("badge_color", theme["badge_color"]),
                icon=data.get("icon", theme["icon"]),
                sample_queries=data.get("sample_queries", [])
            )

    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        return self._agents.get(agent_id.lower().strip())

    def get_all_agents(self) -> List[AgentSummary]:
        default_samples = {
            "antigravity": ["pdf parser", "react testing", "sql optimizer", "fastapi"],
            "claude": ["code review", "mcp server", "playwright testing", "git"],
            "codex": ["unit test generator", "python docstring", "kubernetes", "regex"]
        }
        
        summaries = []
        for agent in self._agents.values():
            samples = agent.sample_queries or default_samples.get(
                agent.id,
                [agent.file_patterns[0].split(".")[0] if agent.file_patterns else "tools", "assistant", "testing"]
            )
            summaries.append(
                AgentSummary(
                    id=agent.id,
                    name=agent.display_name,
                    display_name=agent.display_name,
                    description=agent.description or f"{agent.display_name} instructions and skills",
                    badge_color=agent.badge_color or "indigo",
                    icon=agent.icon or "Sparkles",
                    file_patterns=agent.file_patterns,
                    repo_topics=agent.repo_topics,
                    install_path_hint=agent.install_path_hint,
                    sample_queries=samples
                )
            )
        return summaries

    def get_all_agent_ids(self) -> List[str]:
        return list(self._agents.keys())

config_service = ConfigService()
