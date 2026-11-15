from github_search import (
    load_agents_config,
    _calculate_keyword_score,
    _extract_retry_after,
    _parse_timestamp,
    _search_cache,
    CACHE_TTL,
    search_skills
)

def test_load_config():
    config = load_agents_config()
    assert "antigravity" in config
    assert "claude" in config
    assert "codex" in config
    assert len(config["claude"]["file_patterns"]) > 0
    assert len(config["claude"]["repo_topics"]) > 0
    print("Config loading test passed!")

def test_keyword_scoring():
    repo1 = {
        "name": "pdf-extractor",
        "description": "A tool to parse pdfs",
        "topics": ["pdf", "agent-skills"],
        "matched_files": ["skills/pdf.md"]
    }
    score1 = _calculate_keyword_score(repo1, "pdf")
    # 5 (name) + 4 (topic) + 3 (desc) + 10 (matched_files) + 2 (matched file path) = 24
    assert score1 >= 20

    repo2 = {
        "name": "unrelated-tool",
        "description": "something else",
        "topics": [],
        "matched_files": []
    }
    score2 = _calculate_keyword_score(repo2, "pdf")
    assert score2 == 0
    print("Keyword scoring test passed!")

def test_cache_ttl():
    assert CACHE_TTL == 600
    _search_cache[("test_agent", "kw")] = [{"name": "cached_repo"}]
    assert ("test_agent", "kw") in _search_cache
    assert _search_cache[("test_agent", "kw")][0]["name"] == "cached_repo"
    _search_cache.clear()
    print("Cache TTL test passed!")

def test_timestamp_parser():
    ts1 = _parse_timestamp("2026-11-15T12:00:00Z")
    ts2 = _parse_timestamp("2026-11-10T12:00:00Z")
    assert ts1 > ts2
    print("Timestamp parser test passed!")

if __name__ == "__main__":
    test_load_config()
    test_keyword_scoring()
    test_cache_ttl()
    test_timestamp_parser()
    print("All github_search tests passed successfully!")
