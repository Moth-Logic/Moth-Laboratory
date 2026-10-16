"""
history.py
----------
Historial persistente de operaciones de la calculadora.

Lógica pura (sin GUI): guarda expresiones con su resultado como strings,
manteniendo las entradas más recientes primero y un tope configurable.
El historial se serializa a JSON en disco de forma *best-effort*: si el
archivo no existe, está corrupto o no se puede escribir, la clase sigue
funcionando en memoria — el historial jamás debe romper la app.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# How many entries are kept before the oldest ones are dropped.
DEFAULT_MAX_ENTRIES = 100


def default_history_path() -> Path:
    """Location of the history file for the installed app."""
    return Path.home() / ".everything_app" / "history.json"


@dataclass(frozen=True)
class HistoryEntry:
    """One past operation: the expression as typed, and its result."""
    expression: str
    result: str

    def label(self, max_len: int = 32) -> str:
        """Render 'expr = result' for a compact UI row, truncating if needed."""
        text = f"{self.expression} = {self.result}"
        if max_len is not None and len(text) > max_len:
            return text[: max_len - 1] + "…"
        return text


class History:
    """A capped, persistent list of past calculations (newest first).

    Usage:
        history = History()                      # persistent default path
        history = History(path=None...)          # custom path (tests)
        history.add("2 + 2", "4")
        for entry in history.entries: ...        # newest first
        history.clear()
    """

    def __init__(
        self,
        path: Path | str | None = None,
        max_entries: int = DEFAULT_MAX_ENTRIES,
    ) -> None:
        self._path = Path(path) if path is not None else default_history_path()
        self._max_entries = max(1, int(max_entries))
        self._entries: list[HistoryEntry] = []
        self._load()

    @property
    def path(self) -> Path:
        """File backing this history (JSON)."""
        return self._path

    @property
    def entries(self) -> list[HistoryEntry]:
        """All entries, newest first."""
        return list(self._entries)

    def add(self, expression: str, result: str) -> HistoryEntry:
        """Record a calculation and persist the history (best-effort)."""
        entry = HistoryEntry(str(expression), str(result))
        self._entries.insert(0, entry)     # newest first
        del self._entries[self._max_entries:]  # enforce the cap
        self._save()
        return entry

    def clear(self) -> None:
        """Drop every entry and persist the empty history."""
        self._entries.clear()
        self._save()

    # --- Persistence (best-effort: never raises) --------------------------

    def _load(self) -> None:
        try:
            raw = self._path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, ValueError):
            self._entries = []  # missing or corrupt file — start fresh
            return

        entries: list[HistoryEntry] = []
        if isinstance(data, list):
            for item in data[: self._max_entries]:
                if (
                    isinstance(item, dict)
                    and "expression" in item
                    and "result" in item
                ):
                    entries.append(
                        HistoryEntry(str(item["expression"]), str(item["result"]))
                    )
        self._entries = entries

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = [
                {"expression": e.expression, "result": e.result}
                for e in self._entries
            ]
            self._path.write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
        except OSError:
            pass  # read-only disk etc. — history stays in memory only
