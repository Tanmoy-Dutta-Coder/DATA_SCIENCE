"""Turn a free-text query into a compact, editable search intent."""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional


CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "into",
    "is", "of", "on", "or", "the", "to", "with", "skill", "skills", "tool",
    "tools", "ai", "assistant", "agent", "agents",
}
TYPO_FIXES = {
    "pyhton": "python",
    "pythn": "python",
    "javascrpt": "javascript",
    "javascipt": "javascript",
    "kubernets": "kubernetes",
    "kuberentes": "kubernetes",
    "automatoin": "automation",
    "documemt": "document",
    "reasearch": "research",
    "playwrite": "playwright",
    "claud": "claude",
    "cluade": "claude",
    "antigravty": "antigravity",
}
AGENT_ALIASES = {
    "claude": ("claude", "anthropic", "anthropic claude"),
    "codex": ("codex", "openai", "openai codex", "copilot", "github copilot"),
    "antigravity": ("antigravity", "google antigravity", "gemini", "gemini antigravity"),
}


def _load_json(filename: str) -> dict:
    path = CONFIG_DIR / filename
    try:
        with path.open("r", encoding="utf-8") as source:
            payload = json.load(source)
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _correct_typos(text: str) -> str:
    return re.sub(r"\b[\w'-]+\b", lambda match: TYPO_FIXES.get(match.group(0), match.group(0)), text)


def _agent_aliases() -> Dict[str, List[str]]:
    aliases = {agent: list(names) for agent, names in AGENT_ALIASES.items()}
    config = _load_json("agents.json")
    agents = config.get("agents", config)
    if isinstance(agents, dict):
        for agent_id, data in agents.items():
            if not isinstance(data, dict):
                continue
            aliases.setdefault(agent_id.lower(), []).append(agent_id.lower())
            for key in ("name", "display_name"):
                name = data.get(key)
                if isinstance(name, str) and name.strip():
                    aliases[agent_id.lower()].append(name.lower())
    return aliases


def _detect_agent(text: str) -> Optional[str]:
    matches = []
    for agent, names in _agent_aliases().items():
        for alias in set(names):
            pattern = r"(?<![\w])" + re.escape(alias) + r"(?![\w])"
            found = re.search(pattern, text)
            if found:
                matches.append((found.start(), -len(alias), agent))
    return min(matches)[2] if matches else None


def _remove_agent_names(text: str, agent: Optional[str]) -> str:
    if not agent:
        return text
    aliases = sorted(set(_agent_aliases().get(agent, [agent])), key=len, reverse=True)
    for alias in aliases:
        pattern = r"(?<![\w])" + re.escape(alias) + r"(?![\w])"
        text = re.sub(pattern, " ", text)
    return " ".join(text.split())


def _expand_synonyms(core: str, synonyms_map: dict) -> List[str]:
    core_lower = core.lower()
    expansions: List[str] = []
    for phrase, values in synonyms_map.items():
        phrase = str(phrase).lower().strip()
        if not phrase or not re.search(r"(?<![\w])" + re.escape(phrase) + r"(?![\w])", core_lower):
            continue
        values = [values] if isinstance(values, str) else values
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, str):
                candidate = " ".join(value.lower().split())
                if candidate and candidate != phrase and candidate not in expansions:
                    expansions.append(candidate)
    return expansions


def _detect_category(text: str, categories: dict) -> Optional[str]:
    haystack = f" {text.lower()} "
    matches = []
    for category, keywords in categories.items():
        if isinstance(keywords, str):
            keywords = [keywords]
        if not isinstance(keywords, list):
            continue
        found = {str(keyword).strip().lower() for keyword in keywords
                 if str(keyword).strip() and re.search(r"(?<![\w])" + re.escape(str(keyword).strip().lower()) + r"(?![\w])", haystack)}
        if found:
            matches.append((-len(found), str(category)))
    return min(matches)[1] if matches else None


def understand(query: str) -> dict:
    """Return ``{core, synonyms, category, agent}`` for an input query."""
    corrected = _correct_typos(" ".join((query or "").lower().split())[:200])
    agent = _detect_agent(corrected)
    without_agent = _remove_agent_names(corrected, agent)
    tokens = re.findall(r"[\w.-]+", without_agent, flags=re.UNICODE)
    core = " ".join(token for token in tokens if token not in STOPWORDS)

    synonyms = _expand_synonyms(core, _load_json("synonyms.json"))
    category_text = " ".join([core, *synonyms])
    category = _detect_category(category_text, _load_json("categories.json"))
    return {"core": core, "synonyms": synonyms, "category": category, "agent": agent}


def fts_query(core: str, synonyms: Optional[List[str]] = None) -> str:
    """Build a safely quoted FTS5 query; synonyms are alternatives to the core phrase."""
    def phrase_expression(phrase: str) -> str:
        tokens = re.findall(r"[\w.-]+", phrase.lower(), flags=re.UNICODE)
        return " AND ".join('"' + token.replace('"', '""') + '"*' for token in tokens)

    core_expression = phrase_expression(core)
    alternatives = [phrase_expression(item) for item in (synonyms or [])]
    alternatives = [item for item in alternatives if item]
    if not core_expression:
        return " OR ".join(f"({item})" for item in alternatives)
    if not alternatives:
        return core_expression
    return f"({core_expression}) OR (" + " OR ".join(alternatives) + ")"
