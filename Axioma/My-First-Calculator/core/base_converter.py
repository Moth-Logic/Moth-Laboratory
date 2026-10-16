"""
base_converter.py
------------------
Converts integer values between decimal, binary, octal, and hexadecimal.
No dependencies on GUI or other core modules — pure logic.
"""

from __future__ import annotations


class BaseConverterError(Exception):
    """Raised when the input cannot be parsed in the given base."""


# Supported bases and their labels
BASES = {
    "DEC": 10,
    "BIN": 2,
    "OCT": 8,
    "HEX": 16,
}

_VALID_HEX = frozenset("0123456789abcdefABCDEF")


def parse(value: str, base: int) -> int:
    """Parse *value* (a string) in the given *base* and return an int.

    Raises BaseConverterError on invalid input.
    """
    value = value.strip()
    if not value:
        raise BaseConverterError("Empty input")

    try:
        result = int(value, base)
    except ValueError:
        raise BaseConverterError(
            f"'{value}' is not a valid number in base {base}"
        ) from None
    return result


def convert(value: str, from_base: int) -> dict[str, str]:
    """Convert *value* (string in *from_base*) to all supported bases.

    Returns a dict like {"DEC": "255", "BIN": "11111111", ...}.
    Raises BaseConverterError on invalid input.
    """
    integer = parse(value, from_base)
    return to_all_bases(integer)


def to_all_bases(value: int) -> dict[str, str]:
    """Convert an int to all supported base representations."""
    if value < 0:
        # Plain sign prefix ("-1010") — keeps every representation
        # re-parsable by parse(), so conversions round-trip correctly.
        abs_val = abs(value)
        return {
            "DEC": str(value),
            "BIN": "-" + bin(abs_val)[2:],
            "OCT": "-" + oct(abs_val)[2:],
            "HEX": "-" + hex(abs_val)[2:].upper(),
        }
    return {
        "DEC": str(value),
        "BIN": bin(value)[2:],
        "OCT": oct(value)[2:],
        "HEX": hex(value)[2:].upper(),
    }
