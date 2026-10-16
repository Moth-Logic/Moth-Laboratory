"""Tests for core.ascii_table (generation + search)."""

from __future__ import annotations

import unittest

from core import generate_table, search_table


class TestAsciiTable(unittest.TestCase):
    def test_full_table(self) -> None:
        rows = generate_table()
        self.assertEqual(len(rows), 128)
        self.assertEqual(rows[0],
                         {"DEC": "0", "HEX": "00", "OCT": "000",
                          "BIN": "00000000", "CHAR": "NUL"})
        self.assertEqual(rows[65]["CHAR"], "A")
        self.assertEqual(rows[65]["DEC"], "65")
        self.assertEqual(rows[127]["CHAR"], "DEL")

    def test_search_is_case_insensitive_substring(self) -> None:
        results = search_table("65")
        self.assertIn("65", [r["DEC"] for r in results])
        results = search_table("lf")
        self.assertIn("10", [r["DEC"] for r in results if r["CHAR"] == "LF"])

    def test_search_by_char(self) -> None:
        results = search_table("A")
        self.assertIn("65", [r["DEC"] for r in results])

    def test_empty_query_returns_everything(self) -> None:
        self.assertEqual(search_table("  "), generate_table())

    def test_no_match_returns_empty(self) -> None:
        self.assertEqual(search_table("ZZZZ"), [])


if __name__ == "__main__":
    unittest.main()
