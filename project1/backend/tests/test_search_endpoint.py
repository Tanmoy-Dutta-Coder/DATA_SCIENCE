import re
from unittest.mock import patch
from fastapi import Response, HTTPException

from app.api.routes import search_skills_endpoint
from github_search import GitHubRateLimitError, GitHubSearchError

def run_coro(coro):
    """Executes a coroutine stack synchronously without socket/loop dependencies."""
    stack = [coro]
    val = None
    while stack:
        try:
            val = stack[-1].send(val)
            if hasattr(val, "send"):
                stack.append(val)
                val = None
        except StopIteration as e:
            stack.pop()
            val = e.value
    return val

def test_search_endpoint_success_comma():
    fake_results = [
        {
            "name": "pdf-parser",
            "owner": "testowner",
            "description": "Extract forms from PDF",
            "stars": 42,
            "last_updated": "2026-11-15T00:00:00Z",
            "html_url": "https://github.com/testowner/pdf-parser",
            "matched_files": ["skills/pdf.md"]
        }
    ]

    async def fake_search(agent, keywords):
        assert agent == "claude"
        assert keywords == "pdf forms"
        return fake_results

    with patch("app.api.routes.search_skills", side_effect=fake_search):
        resp = Response()
        data = run_coro(search_skills_endpoint(response=resp, agent="claude", q="pdf,forms"))
        assert data["agent"] == "claude"
        assert data["keywords"] == ["pdf", "forms"]
        assert data["count"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "pdf-parser"
        print("Success comma-separated test passed!")

def test_search_endpoint_max_five_keywords():
    async def fake_search(agent, keywords):
        assert agent == "antigravity"
        assert keywords == "one two three four five"
        return []

    with patch("app.api.routes.search_skills", side_effect=fake_search):
        resp = Response()
        data = run_coro(search_skills_endpoint(
            response=resp,
            agent="antigravity",
            q="one, two three,four, five, six, seven"
        ))
        assert len(data["keywords"]) == 5
        assert data["keywords"] == ["one", "two", "three", "four", "five"]
        print("Max 5 keywords test passed!")

def test_search_endpoint_invalid_agent_400():
    resp = Response()
    try:
        run_coro(search_skills_endpoint(response=resp, agent="unknown_agent", q="test"))
        assert False, "Should have raised HTTPException"
    except HTTPException as he:
        assert he.status_code == 400
        assert "does not exist in configuration" in he.detail
        print("Invalid agent 400 error test passed!")

def test_search_endpoint_rate_limit_429():
    async def fake_search(agent, keywords):
        raise GitHubRateLimitError("Rate limit exceeded", retry_after=45)

    with patch("app.api.routes.search_skills", side_effect=fake_search):
        resp = Response()
        try:
            run_coro(search_skills_endpoint(response=resp, agent="codex", q="python"))
            assert False, "Should have raised HTTPException"
        except HTTPException as he:
            assert he.status_code == 429
            assert "Retry after 45 seconds" in he.detail
            assert resp.headers.get("Retry-After") == "45"
            print("Rate limit 429 error test passed!")

def test_search_endpoint_github_down_502():
    async def fake_search(agent, keywords):
        raise GitHubSearchError("Network unreachable")

    with patch("app.api.routes.search_skills", side_effect=fake_search):
        resp = Response()
        try:
            run_coro(search_skills_endpoint(response=resp, agent="claude", q="test"))
            assert False, "Should have raised HTTPException"
        except HTTPException as he:
            assert he.status_code == 502
            assert "GitHub service unavailable" in he.detail
            print("GitHub down 502 error test passed!")

if __name__ == "__main__":
    test_search_endpoint_success_comma()
    test_search_endpoint_max_five_keywords()
    test_search_endpoint_invalid_agent_400()
    test_search_endpoint_rate_limit_429()
    test_search_endpoint_github_down_502()
    print("All search endpoint unit tests passed successfully!")
