"""FTS5 candidate retrieval, configurable ranking, explanations, and facets."""
import json
import math
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .query_understanding import STOPWORDS, fts_query


RANKING_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "ranking_config.json"
FIELD_LABELS = {"name": "Name", "tags": "Tags", "description": "Description", "skill_text": "Skill text"}
FTS_COLUMN_ORDER = ("name", "description", "tags", "skill_text")


def load_ranking_config(path: Path = RANKING_CONFIG_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as source:
        config = json.load(source)
    weights = config["weights"]
    if not math.isclose(sum(float(value) for value in weights.values()), 1.0, abs_tol=0.0001):
        raise ValueError("Ranking weights in ranking_config.json must sum to 1.0.")
    field_weights = config["text_field_weights"]
    if not math.isclose(sum(float(value) for value in field_weights.values()), 1.0, abs_tol=0.0001):
        raise ValueError("Text field weights in ranking_config.json must sum to 1.0.")
    return config


def retrieve_candidates(db: sqlite3.Connection, intent: Dict[str, Any], limit: Optional[int] = None,
                        config: Optional[Dict[str, Any]] = None,
                        agent_filter: Optional[str] = None) -> Tuple[List[sqlite3.Row], int]:
    config = config or load_ranking_config()
    core = intent.get("core", "")
    synonyms = intent.get("synonyms", [])
    match_query = fts_query(core, synonyms)
    if not match_query:
        return [], 0
    candidate_limit = min(limit or config["limits"]["candidates"], config["limits"]["candidates"])
    field_weights = config["text_field_weights"]
    bm25_args = ",".join("?" for _ in FTS_COLUMN_ORDER)
    sql = f"""SELECT s.*, bm25(skills_fts,{bm25_args}) AS fts_relevance,
                      COALESCE(fb.feedback_count,0) AS feedback_count
               FROM skills_fts JOIN skills s ON s.skill_id=skills_fts.rowid
               LEFT JOIN (SELECT skill_id,COUNT(*) AS feedback_count FROM feedback GROUP BY skill_id) fb
                 ON fb.skill_id=s.skill_id
               WHERE skills_fts MATCH ?"""
    params = [float(field_weights[field]) for field in FTS_COLUMN_ORDER]
    params.append(match_query)
    count_sql = """SELECT COUNT(DISTINCT s.repo || char(31) || s.agent)
                          FROM skills_fts JOIN skills s ON s.skill_id=skills_fts.rowid
                          WHERE skills_fts MATCH ?"""
    if agent_filter:
        sql += " AND s.agent=?"
        count_sql += " AND s.agent=?"
        params.append(agent_filter)
    sql += " ORDER BY fts_relevance ASC LIMIT ?"
    params.append(candidate_limit)
    candidates = db.execute(sql, params).fetchall()
    count_params = [match_query] + ([agent_filter] if agent_filter else [])
    count = db.execute(count_sql, count_params).fetchone()[0]
    return candidates, count


def _tokens(text: Any) -> set[str]:
    # Hyphens and dots separate natural-language terms (e.g. ``video-generation``).
    return {token for token in re.findall(r"[\w]+", str(text or "").lower(), flags=re.UNICODE)
            if token not in STOPWORDS}


def _matches(query_tokens: Sequence[str], field_tokens: set[str]) -> List[str]:
    return [token for token in query_tokens if any(value == token or value.startswith(token) for value in field_tokens)]


def _text_scores(row: Dict[str, Any], intent: Dict[str, Any], config: Dict[str, Any]):
    core_tokens = sorted(_tokens(intent.get("core", "")))
    synonym_phrases = [sorted(_tokens(value)) for value in intent.get("synonyms", [])]
    synonym_phrases = [phrase for phrase in synonym_phrases if phrase]
    field_scores: Dict[str, float] = {}
    field_hits: Dict[str, List[str]] = {}
    for field in config["text_field_weights"]:
        field_tokens = _tokens(row.get(field))
        core_hits = _matches(core_tokens, field_tokens)
        alternatives = [(len(_matches(phrase, field_tokens)) / len(phrase), _matches(phrase, field_tokens))
                       for phrase in synonym_phrases]
        synonym_score, synonym_hits = max(alternatives, default=(0.0, []), key=lambda value: value[0])
        core_score = len(core_hits) / len(core_tokens) if core_tokens else 0.0
        synonym_score *= float(config["normalization"].get("synonym_relevance_factor", 1.0))
        if core_score >= synonym_score:
            field_scores[field] = core_score
            field_hits[field] = core_hits
        else:
            field_scores[field] = synonym_score
            field_hits[field] = synonym_hits
    return field_scores, field_hits


def _age_days(value: Optional[str], now: datetime) -> Optional[int]:
    if not value:
        return None
    try:
        updated = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        return max(0, (now - updated.astimezone(timezone.utc)).days)
    except (ValueError, TypeError):
        return None


def _score_group(row: Dict[str, Any], field_scores: Dict[str, float], field_hits: Dict[str, List[str]],
                 feedback_count: int, preferred_agent: Optional[str], intent: Dict[str, Any],
                 config: Dict[str, Any], now: datetime) -> Dict[str, Any]:
    weights = config["weights"]
    text_relevance = sum(config["text_field_weights"][field] * field_scores.get(field, 0.0)
                         for field in config["text_field_weights"])
    agent_match = float(bool(preferred_agent) and row["agent"] == preferred_agent)
    stars_cap = max(1.0, float(config["normalization"]["stars_log_max"]))
    stars = max(0, int(row.get("stars") or 0))
    star_score = min(1.0, math.log1p(stars) / math.log1p(stars_cap))
    age_days = _age_days(row.get("last_updated"), now)
    half_life = max(1.0, float(config["normalization"]["recency_half_life_days"]))
    recency = math.exp(-math.log(2) * age_days / half_life) if age_days is not None else 0.0
    feedback_cap = max(1.0, float(config["normalization"]["feedback_log_max"]))
    feedback_score = min(1.0, math.log1p(max(0, feedback_count)) / math.log1p(feedback_cap))
    category = intent.get("category")
    category_match = float(str(row.get("category") or "").lower() == str(category).lower()) if category else 0.0
    components = {
        "text_relevance": text_relevance,
        "agent_match": agent_match,
        "log_scaled_stars": star_score,
        "recency": recency,
        "feedback_popularity": feedback_score,
        "category_match": category_match,
    }
    score = sum(weights[name] * components[name] for name in weights)
    penalties = config["penalties"]
    reasons = []
    for field, label in FIELD_LABELS.items():
        hits = field_hits.get(field, [])
        if hits:
            reasons.append(f"{label} matches: {', '.join(hits[:5])}")
    if agent_match and preferred_agent:
        reasons.append(f"Agent matches {preferred_agent}")
    if category_match and category:
        reasons.append(f"Category matches {category}")
    if stars:
        reasons.append(f"Popularity: {stars:,} stars")
    if age_days is not None and age_days < 365:
        reasons.append("Updated within the last year")
    if feedback_count:
        reasons.append(f"Popular with users: {feedback_count} feedback actions")
    archived = bool(row.get("archived"))
    stale_days = int(penalties["stale_days"])
    stale = age_days is not None and age_days >= stale_days
    penalty_value = 0.0
    if archived:
        penalty_value += float(penalties["archived"])
        reasons.append("Archived repository penalty applied")
    if stale:
        penalty_value += float(penalties["stale_2y"])
        reasons.append("No update in 2+ years penalty applied")
    score = max(0.0, score - penalty_value)
    tags = row.get("tags") or "[]"
    try:
        tags = json.loads(tags) if isinstance(tags, str) else tags
    except json.JSONDecodeError:
        tags = [tags]
    matched_files = sorted(row.get("matched_files", set()))
    return {
        "id": row["skill_id"], "skill_id": row["skill_id"], "name": row["name"],
        "owner": row["owner"], "repo": row["repo"], "agent": row["agent"],
        "category": row.get("category"), "description": row.get("description") or "",
        "stars": stars, "forks": int(row.get("forks") or 0),
        "last_updated": row.get("last_updated") or "", "archived": archived,
        "license": row.get("license"), "install_path": row.get("install_path") or "",
        "html_url": f"https://github.com/{row['repo']}", "matched_files": matched_files,
        "topics": tags, "language": None, "score": round(score, 6), "why_matched": reasons,
        "score_breakdown": {key: round(value, 6) for key, value in components.items()},
        "penalties": round(penalty_value, 6), "feedback_count": feedback_count,
        "_field_scores": field_scores, "_field_hits": field_hits,
    }


def rank_candidates(rows: Sequence[sqlite3.Row], intent: Dict[str, Any], preferred_agent: Optional[str],
                    config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    config = config or load_ranking_config()
    now = datetime.now(timezone.utc)
    grouped: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for raw in rows:
        row = dict(raw)
        field_scores, field_hits = _text_scores(row, intent, config)
        key = (row["repo"], row["agent"])
        current = grouped.get(key)
        if current is None:
            row["matched_files"] = {row.get("skill_file_path", "")} - {""}
            row["_best_text"] = sum(config["text_field_weights"][field] * field_scores[field]
                                    for field in config["text_field_weights"])
            row["_field_scores"] = field_scores
            row["_field_hits"] = field_hits
            row["feedback_count"] = int(row.get("feedback_count") or 0)
            grouped[key] = row
            continue
        path = row.get("skill_file_path", "")
        if path:
            current["matched_files"].add(path)
        current["feedback_count"] += int(row.get("feedback_count") or 0)
        for field, value in field_scores.items():
            if value > current["_field_scores"].get(field, 0.0):
                current["_field_scores"][field] = value
                current["_field_hits"][field] = field_hits[field]
        text_score = sum(config["text_field_weights"][field] * current["_field_scores"][field]
                         for field in config["text_field_weights"])
        if text_score > current["_best_text"]:
            for field in ("skill_id", "name", "description", "category", "last_updated", "license", "install_path"):
                current[field] = row.get(field)
            current["_best_text"] = text_score

    ranked = []
    for row in grouped.values():
        result = _score_group(row, row["_field_scores"], row["_field_hits"], row["feedback_count"],
                              preferred_agent, intent, config, now)
        result.pop("_field_scores", None)
        result.pop("_field_hits", None)
        ranked.append(result)
    return sorted(ranked, key=lambda result: (result["score"], result["stars"]), reverse=True)


def build_facets(results: Sequence[Dict[str, Any]], config: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, int]]:
    config = config or load_ranking_config()
    facets = {"agent": {}, "category": {}, "stars": {}, "updated": {}}
    now = datetime.now(timezone.utc)
    for result in results:
        for facet, value in (("agent", result.get("agent") or "unknown"),
                             ("category", result.get("category") or "uncategorized")):
            facets[facet][value] = facets[facet].get(value, 0) + 1
        stars = result.get("stars", 0)
        boundaries = config["star_facets"]
        star_bucket = f"{boundaries[-1]}+" if stars >= boundaries[-1] else "0"
        for low, high in zip(boundaries, boundaries[1:]):
            if low <= stars < high:
                star_bucket = f"{low}-{high - 1}"
                break
        facets["stars"][star_bucket] = facets["stars"].get(star_bucket, 0) + 1
        age = _age_days(result.get("last_updated"), now)
        updated_bucket = ("unknown" if age is None else "30d" if age <= 30 else "1y" if age <= 365
                         else "2y" if age <= 730 else "older")
        facets["updated"][updated_bucket] = facets["updated"].get(updated_bucket, 0) + 1
    return facets


def search_catalog(db: sqlite3.Connection, intent: Dict[str, Any], preferred_agent: Optional[str],
                   page: int = 1, per_page: int = 20, category: Optional[str] = None,
                   min_stars: Optional[int] = None, updated: Optional[str] = None,
                   sort: str = "relevance") -> Dict[str, Any]:
    config = load_ranking_config()
    rows, total_count = retrieve_candidates(db, intent, config=config, agent_filter=preferred_agent)
    ranked = rank_candidates(rows, intent, preferred_agent, config)
    facets = build_facets(ranked, config)
    category_filter = (category or "").strip().lower()
    updated_filter = (updated or "").strip().lower()
    filtered = [result for result in ranked
                if (not category_filter or str(result.get("category") or "").lower() == category_filter)
                and (min_stars is None or result["stars"] >= min_stars)
                and (not updated_filter or _updated_matches(result.get("last_updated"), updated_filter))]
    if sort == "stars":
        filtered.sort(key=lambda result: (result["stars"], result["score"]), reverse=True)
    elif sort == "recent":
        filtered.sort(key=lambda result: (result["last_updated"], result["score"]), reverse=True)
    else:
        filtered.sort(key=lambda result: (result["score"], result["stars"]), reverse=True)
    result_limit = min(max(1, per_page), int(config["limits"]["results"]))
    offset = (max(1, page) - 1) * result_limit
    return {"results": filtered[offset:offset + result_limit], "count": len(filtered), "total_count": total_count,
            "candidate_count": len(rows), "facets": facets}


def _updated_matches(value: Optional[str], updated_filter: str) -> bool:
    now = datetime.now(timezone.utc)
    age = _age_days(value, now)
    if updated_filter == "unknown":
        return age is None
    if age is None:
        return False
    if updated_filter == "30d":
        return age <= 30
    if updated_filter == "1y":
        return age <= 365
    if updated_filter == "2y":
        return age <= 730
    if updated_filter == "older":
        return age > 730
    return False
