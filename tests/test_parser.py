"""Unit tests for src/parser.py."""

import unittest
from src.parser import extract_candidate_statements, unescape_and_strip_html


class TestParser(unittest.TestCase):
    def test_double_escaped_html_entities_are_cleaned(self) -> None:
        raw = (
            "&lt;div class=&quot;content&quot;&gt;"
            "&lt;p&gt;Perform monthly balance sheet reconciliations &amp;amp; update Excel trackers.&lt;/p&gt;"
            "&lt;/div&gt;"
        )
        cleaned = unescape_and_strip_html(raw)
        self.assertIn("Perform monthly balance sheet reconciliations & update Excel trackers.", cleaned)
        self.assertNotIn("&lt;", cleaned)
        self.assertNotIn("<p>", cleaned)

    def test_list_items_split_into_separate_statements(self) -> None:
        raw = (
            "&lt;ul&gt;"
            "&lt;li&gt;Maintain accurate records in Salesforce CRM for all renewals.&lt;/li&gt;"
            "&lt;li&gt;Proficiency in Excel and Google Sheets is required.&lt;/li&gt;"
            "&lt;/ul&gt;"
        )
        statements = extract_candidate_statements(raw)
        self.assertEqual(len(statements), 2)
        self.assertEqual(
            statements[0],
            "Maintain accurate records in Salesforce CRM for all renewals.",
        )
        self.assertEqual(
            statements[1],
            "Proficiency in Excel and Google Sheets is required.",
        )

    def test_abbreviations_do_not_break_sentence_splitting(self) -> None:
        raw = (
            "&lt;p&gt;Use AI-driven tools (e.g. automated reconciliation workflows) "
            "to reduce manual effort across U.S. entities.&lt;/p&gt;"
        )
        statements = extract_candidate_statements(raw)
        self.assertEqual(len(statements), 1)
        self.assertIn("e.g. automated reconciliation workflows", statements[0])


if __name__ == "__main__":
    unittest.main()
