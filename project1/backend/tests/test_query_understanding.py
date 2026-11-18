"""Unit tests for query normalization and editable search intent maps."""
import unittest

from app.services.query_understanding import fts_query, understand


class QueryUnderstandingTests(unittest.TestCase):
    def test_lowercase_typos_and_stopwords(self):
        result = understand("  PYHTON skills for the AI tool  ")
        self.assertEqual(result, {
            "core": "python",
            "synonyms": [],
            "category": "development",
            "agent": None,
        })

    def test_expand_synonyms_from_json(self):
        result = understand("pdf parser")
        self.assertEqual(result["core"], "pdf parser")
        self.assertEqual(result["synonyms"], ["portable document format"])

    def test_detect_category_from_keyword_map(self):
        result = understand("pdf parser")
        self.assertEqual(result["category"], "documents")

    def test_detect_agent_and_remove_agent_name_from_core(self):
        result = understand("Anthropic Claude PDF skills for the")
        self.assertEqual(result["agent"], "claude")
        self.assertEqual(result["core"], "pdf")
        self.assertEqual(result["category"], "documents")

    def test_unknown_agent_and_empty_normalized_query(self):
        result = understand("the AI tools for a")
        self.assertEqual(result, {"core": "", "synonyms": [], "category": None, "agent": None})

    def test_fts_query_uses_core_and_synonyms_as_alternatives(self):
        query = fts_query("pdf parser", ["portable document format"])
        self.assertEqual(query, '("pdf"* AND "parser"*) OR ("portable"* AND "document"* AND "format"*)')


if __name__ == "__main__":
    unittest.main(verbosity=2)
