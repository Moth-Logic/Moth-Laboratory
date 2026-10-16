"""
ascii_table.py
--------------
Generates the full 7-bit ASCII table (codes 0-127) as a list of dicts.
Pure data — no GUI dependencies.
"""

from __future__ import annotations

# Control characters that have no printable representation
_CONTROL_NAMES = {
    0: "NUL", 1: "SOH", 2: "STX", 3: "ETX", 4: "EOT", 5: "ENQ",
    6: "ACK", 7: "BEL", 8: "BS", 9: "TAB", 10: "LF", 11: "VT",
    12: "FF", 13: "CR", 14: "SO", 15: "SI", 16: "DLE", 17: "DC1",
    18: "DC2", 19: "DC3", 20: "DC4", 21: "NAK", 22: "SYN", 23: "ETB",
    24: "CAN", 25: "EM", 26: "SUB", 27: "ESC", 28: "FS", 29: "GS",
    30: "RS", 31: "US", 127: "DEL",
}


def _char_display(code: int) -> str:
    """Return a display-friendly string for an ASCII code."""
    if code in _CONTROL_NAMES:
        return _CONTROL_NAMES[code]
    return chr(code)


def generate_table() -> list[dict[str, str]]:
    """Return the full ASCII table as a list of row dicts.

    Each row has keys: DEC, HEX, OCT, BIN, CHAR.
    """
    rows: list[dict[str, str]] = []
    for code in range(128):
        rows.append({
            "DEC": str(code),
            "HEX": f"{code:02X}",
            "OCT": f"{code:03o}",
            "BIN": f"{code:08b}",
            "CHAR": _char_display(code),
        })
    return rows


def search_table(query: str) -> list[dict[str, str]]:
    """Search the ASCII table by decimal code, hex, char, or name.

    Returns matching rows. The query is matched as a substring (case-insensitive).
    """
    query_lower = query.lower().strip()
    if not query_lower:
        return generate_table()

    results: list[dict[str, str]] = []
    for row in generate_table():
        # Match against any field
        searchable = " ".join(row.values()).lower()
        if query_lower in searchable:
            results.append(row)
    return results
