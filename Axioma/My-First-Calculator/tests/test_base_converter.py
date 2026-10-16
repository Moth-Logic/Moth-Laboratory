"""Tests for core.base_converter — includes the negative round-trip
regression (bug 3: outputs used to render as '-bin1010', which could not
be parsed back)."""

from __future__ import annotations

import unittest

from core import BASES, BaseConverterError, convert, parse, to_all_bases


class TestParse(unittest.TestCase):
    def test_parses_valid_values(self) -> None:
        self.assertEqual(parse("255", 10), 255)
        self.assertEqual(parse("11111111", 2), 255)
        self.assertEqual(parse("ff", 16), 255)
        self.assertEqual(parse("0xFF", 16), 255)

    def test_rejects_invalid_values(self) -> None:
        for value, base in [("", 10), ("abc", 10), ("2", 2), ("G", 16), ("9", 8)]:
            with self.subTest(value=value, base=base):
                with self.assertRaises(BaseConverterError):
                    parse(value, base)

    def test_empty_is_rejected(self) -> None:
        with self.assertRaises(BaseConverterError):
            parse("   ", 10)


class TestConvert(unittest.TestCase):
    def test_positive_conversions(self) -> None:
        self.assertEqual(
            convert("255", 10),
            {"DEC": "255", "BIN": "11111111", "OCT": "377", "HEX": "FF"},
        )
        self.assertEqual(convert("1010", 2)["DEC"], "10")

    def test_zero(self) -> None:
        self.assertEqual(
            to_all_bases(0),
            {"DEC": "0", "BIN": "0", "OCT": "0", "HEX": "0"},
        )

    def test_negative_outputs_are_re_parsable(self) -> None:
        # Regression (bug 3): negatives used to render as "-bin1010".
        result = convert("-10", 10)
        self.assertEqual(
            result,
            {"DEC": "-10", "BIN": "-1010", "OCT": "-12", "HEX": "-A"},
        )
        self.assertEqual(parse(result["DEC"], BASES["DEC"]), -10)
        self.assertEqual(parse(result["BIN"], BASES["BIN"]), -10)
        self.assertEqual(parse(result["OCT"], BASES["OCT"]), -10)
        self.assertEqual(parse(result["HEX"], BASES["HEX"]), -10)

    def test_invalid_input_raises(self) -> None:
        with self.assertRaises(BaseConverterError):
            convert("not-a-number", 10)


if __name__ == "__main__":
    unittest.main()
