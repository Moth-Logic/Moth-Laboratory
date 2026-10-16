"""Tests for core.history (persistence, capping, corruption recovery)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core import History, HistoryEntry


class TestHistory(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "history.json"

    def test_add_returns_entry_and_lists_newest_first(self) -> None:
        history = History(path=self.path)
        history.add("2 + 2", "4")
        history.add("10 / 2", "5")
        entries = history.entries
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0], HistoryEntry("10 / 2", "5"))
        self.assertEqual(entries[1], HistoryEntry("2 + 2", "4"))

    def test_entries_property_is_a_copy(self) -> None:
        history = History(path=self.path)
        history.add("1 + 1", "2")
        history.entries.clear()
        self.assertEqual(len(history.entries), 1)

    def test_cap_drops_oldest(self) -> None:
        history = History(path=self.path, max_entries=3)
        for i in range(5):
            history.add(f"{i} + {i}", str(i * 2))
        entries = history.entries
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].expression, "4 + 4")   # newest kept
        self.assertEqual(entries[-1].expression, "2 + 2")  # oldest dropped

    def test_persists_across_instances(self) -> None:
        History(path=self.path).add("3 * 3", "9")
        reloaded = History(path=self.path)
        self.assertEqual(reloaded.entries, [HistoryEntry("3 * 3", "9")])

    def test_clear_empties_and_persists(self) -> None:
        history = History(path=self.path)
        history.add("1 + 1", "2")
        history.clear()
        self.assertEqual(history.entries, [])
        self.assertEqual(History(path=self.path).entries, [])

    def test_missing_file_starts_empty(self) -> None:
        self.assertEqual(History(path=self.path).entries, [])

    def test_corrupt_file_starts_empty_without_crashing(self) -> None:
        self.path.write_text("{not json!!", encoding="utf-8")
        history = History(path=self.path)
        self.assertEqual(history.entries, [])
        history.add("1 + 1", "2")  # and it can still save afterwards
        self.assertEqual(len(History(path=self.path).entries), 1)

    def test_malformed_entries_are_skipped(self) -> None:
        self.path.write_text(
            json.dumps([{"expression": "ok", "result": "1"}, "junk", {"nope": 1}]),
            encoding="utf-8",
        )
        self.assertEqual(History(path=self.path).entries,
                         [HistoryEntry("ok", "1")])

    def test_label_truncates(self) -> None:
        entry = HistoryEntry("1234567890" * 6, "42")
        label = entry.label(20)
        self.assertEqual(len(label), 20)
        self.assertTrue(label.endswith("…"))
        self.assertEqual(HistoryEntry("2 + 2", "4").label(20), "2 + 2 = 4")


if __name__ == "__main__":
    unittest.main()
