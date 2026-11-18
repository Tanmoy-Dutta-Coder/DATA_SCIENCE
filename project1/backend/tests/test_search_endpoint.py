"""Endpoint tests for SkillFinder's local-catalog search API."""
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.api.routes import search_skills_endpoint


def run_coro(coro):
    """Run an endpoint coroutine that completes without external I/O."""
    try:
        coro.send(None)
    except StopIteration as result:
        return result.value
    raise AssertionError("Endpoint unexpectedly suspended")


class SearchEndpointTests(unittest.TestCase):
    def test_search_endpoint_success_comma_separated_terms(self):
        expected = {
            "agent": "claude",
            "keywords": ["pdf", "forms"],
            "query": {"core": "pdf forms", "synonyms": [], "category": "documents", "agent": None},
            "count": 1,
            "page": 1,
            "per_page": 20,
            "results": [{"name": "pdf-parser", "owner": "testowner"}],
            "suggestions": [],
            "catalog_updated_at": None,
        }
        with patch("app.api.routes.catalog_service.search", return_value=expected) as search:
            data = run_coro(search_skills_endpoint(agent="claude", q="pdf,forms", category=None,
                                                   min_stars=None, updated=None, sort="relevance", page=1, per_page=20))

        search.assert_called_once_with("claude", "pdf,forms", 1, 20, None, None, None, "relevance")
        self.assertEqual(data["agent"], "claude")
        self.assertEqual(data["keywords"], ["pdf", "forms"])
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "pdf-parser")

    def test_search_endpoint_passes_query_and_pagination_to_catalog(self):
        terms = ["one", "two", "three", "four", "five", "six", "seven"]
        expected = {"agent": "antigravity", "keywords": terms}
        query = "one, two three,four, five, six, seven"
        with patch("app.api.routes.catalog_service.search", return_value=expected) as search:
            data = run_coro(search_skills_endpoint(agent="antigravity", q=query, category=None,
                                                   min_stars=None, updated=None, sort="relevance", page=2, per_page=10))

        search.assert_called_once_with("antigravity", query, 2, 10, None, None, None, "relevance")
        self.assertEqual(data["keywords"], terms)

    def test_search_endpoint_invalid_agent_400(self):
        with self.assertRaises(HTTPException) as error:
            run_coro(search_skills_endpoint(agent="unknown_agent", q="test", page=1, per_page=20))

        self.assertEqual(error.exception.status_code, 400)
        self.assertIn("Supported agents", error.exception.detail)

    def test_search_endpoint_empty_query_400(self):
        with patch("app.api.routes.catalog_service.search", side_effect=ValueError("Enter at least one search term.")) as search:
            with self.assertRaises(HTTPException) as error:
                run_coro(search_skills_endpoint(agent="codex", q="   ", category=None, min_stars=None,
                                                updated=None, sort="relevance", page=1, per_page=20))

        search.assert_called_once_with("codex", "   ", 1, 20, None, None, None, "relevance")
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "Enter at least one search term.")

    def test_search_endpoint_catalog_value_error_is_client_error(self):
        with patch("app.api.routes.catalog_service.search", side_effect=ValueError("Invalid local query")):
            with self.assertRaises(HTTPException) as error:
                run_coro(search_skills_endpoint(agent="claude", q="bad query", category=None, min_stars=None,
                                                updated=None, sort="relevance", page=1, per_page=20))

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "Invalid local query")


if __name__ == "__main__":
    unittest.main(verbosity=2)
