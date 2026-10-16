"""Tests for the Lexer → Parser → Evaluator pipeline (core.Calculator).

Includes regression tests for bugs found during review:
  - a lone '.' must raise LexerError, not a raw ValueError (bug 1)
  - overflow / non-finite results must raise EvaluationError, not leak
    OverflowError (bugs 2 & 4)
"""

from __future__ import annotations

import math
import unittest

from core import (
    ANGLE_DEG,
    ANGLE_RAD,
    Calculator,
    CalculatorError,
    EvaluationError,
    LexerError,
    ParserError,
)
from core.lexer import Lexer


class TestLexer(unittest.TestCase):
    def test_tokens_and_eof(self) -> None:
        tokens = Lexer("2 + 3").tokenize()
        self.assertEqual([t.type.name for t in tokens],
                         ["NUMBER", "PLUS", "NUMBER", "EOF"])

    def test_scientific_notation(self) -> None:
        self.assertEqual(Lexer("1e3").tokenize()[0].value, 1000.0)
        self.assertEqual(Lexer("2.5E-3").tokenize()[0].value, 0.0025)
        self.assertEqual(Lexer("1E+6").tokenize()[0].value, 1_000_000.0)

    def test_e_constant_still_works(self) -> None:
        # 'e' not followed by digits must remain Euler's constant
        tokens = Lexer("2 * e").tokenize()
        self.assertEqual(len(tokens), 4)  # 2, *, e, EOF
        self.assertAlmostEqual(tokens[2].value, math.e)

    def test_lone_dot_is_lexer_error_not_value_error(self) -> None:
        # Regression (bug 1): float('.') used to raise a raw ValueError
        # that escaped the CalculatorError hierarchy.
        with self.assertRaises(LexerError):
            Lexer(".").tokenize()

    def test_malformed_numbers_are_lexer_error(self) -> None:
        # Raw ValueError cases — these blow up inside float() and must be
        # converted to LexerError.
        for bad in (".", ".."):
            with self.subTest(bad=bad):
                with self.assertRaises(LexerError):
                    Lexer(bad).tokenize()

    def test_malformed_numbers_fail_evaluation(self) -> None:
        # These tokenize into adjacent/split numbers — the parser must
        # reject them (never a raw ValueError leaking out).
        for bad in ("1e", "2.5.5", "5..3"):
            with self.subTest(bad=bad):
                with self.assertRaises(CalculatorError):
                    Calculator().evaluate(bad)

    def test_unknown_character(self) -> None:
        with self.assertRaises(LexerError):
            Lexer("@").tokenize()

    def test_constants_case_insensitive(self) -> None:
        tokens = Lexer("PI + E").tokenize()
        self.assertAlmostEqual(tokens[0].value, math.pi)
        self.assertAlmostEqual(tokens[2].value, math.e)


class TestParserAndEvaluator(unittest.TestCase):
    def setUp(self) -> None:
        self.calc = Calculator()

    def eval(self, expression: str) -> float:
        return self.calc.evaluate(expression)

    # --- precedence / associativity (README examples) --------------------

    def test_precedence(self) -> None:
        self.assertEqual(self.eval("2 + 3 * 4"), 14)
        self.assertEqual(self.eval("(2 + 3) * 4"), 20)
        self.assertEqual(self.eval("10 / 2 / 5"), 1)
        self.assertEqual(self.eval("2 * (3 + (4 - 1))"), 12)

    def test_power_is_right_associative(self) -> None:
        self.assertEqual(self.eval("2^3^2"), 512)

    def test_modulo(self) -> None:
        self.assertEqual(self.eval("10 % 3"), 1)
        self.assertEqual(self.eval("2^10"), 1024)

    def test_unary_operators(self) -> None:
        self.assertEqual(self.eval("-5 + 3"), -2)
        self.assertEqual(self.eval("--5"), 5)
        self.assertEqual(self.eval("-(2 + 3)"), -5)

    # --- scientific functions -------------------------------------------

    def test_trig_degrees(self) -> None:
        self.assertEqual(self.calc.angle_mode, ANGLE_DEG)
        self.assertAlmostEqual(self.eval("sin(30)"), 0.5)
        self.assertAlmostEqual(self.eval("cos(60)"), 0.5)
        self.assertAlmostEqual(self.eval("tan(45)"), 1.0)
        self.assertAlmostEqual(self.eval("asin(0.5)"), 30.0)
        self.assertAlmostEqual(self.eval("acos(1)"), 0.0)
        self.assertAlmostEqual(self.eval("atan(1)"), 45.0)

    def test_trig_radians(self) -> None:
        self.calc.angle_mode = ANGLE_RAD
        self.assertEqual(self.calc.angle_mode, ANGLE_RAD)
        self.assertAlmostEqual(self.eval("sin(pi/2)"), 1.0)
        self.assertAlmostEqual(self.eval("cos(0)"), 1.0)
        self.assertAlmostEqual(self.eval("asin(1)"), math.pi / 2)

    def test_angle_mode_switch_back(self) -> None:
        self.calc.angle_mode = ANGLE_RAD
        self.calc.angle_mode = ANGLE_DEG
        self.assertAlmostEqual(self.eval("sin(30)"), 0.5)

    def test_invalid_angle_mode(self) -> None:
        with self.assertRaises(ValueError):
            self.calc.angle_mode = "grad"

    def test_other_functions(self) -> None:
        self.assertEqual(self.eval("sqrt(16) + log(100)"), 6)
        self.assertEqual(self.eval("ceil(3.2) * floor(4.8)"), 16)  # 4 * 4
        self.assertEqual(self.eval("cbrt(-8)"), -2)
        self.assertAlmostEqual(self.eval("ln(e)"), 1.0)
        self.assertEqual(self.eval("abs(-5)"), 5)
        self.assertEqual(self.eval("round(3.6)"), 4)
        self.assertEqual(self.eval("exp(0)"), 1)

    def test_constants(self) -> None:
        self.assertAlmostEqual(self.eval("pi * 2"), 2 * math.pi)
        self.assertAlmostEqual(self.eval("e"), math.e)

    def test_scientific_notation_evaluates(self) -> None:
        self.assertEqual(self.eval("1e3"), 1000)
        self.assertEqual(self.eval("2.5E-3 * 8"), 0.02)
        self.assertEqual(self.eval("1e2 * 2"), 200)


class TestErrors(unittest.TestCase):
    """Every input problem must surface as CalculatorError with a message."""

    def setUp(self) -> None:
        self.calc = Calculator()

    def assert_eval_error(self, expression: str, cls, fragment: str | None = None):
        with self.assertRaises(cls) as ctx:
            self.calc.evaluate(expression)
        if fragment is not None:
            self.assertIn(fragment, str(ctx.exception))
        return ctx.exception

    def test_division_by_zero(self) -> None:
        self.assert_eval_error("5 / 0", EvaluationError, "División entre cero")

    def test_modulo_by_zero(self) -> None:
        self.assert_eval_error("5 % 0", EvaluationError, "Módulo por cero")

    def test_overflow_power(self) -> None:
        # Regression (bug 2/4 family): overflow must be EvaluationError
        self.assert_eval_error("10^400", EvaluationError)

    def test_function_overflow(self) -> None:
        # Regression (bug 4): exp(1000) raised a bare OverflowError
        self.assert_eval_error("exp(1000)", EvaluationError, "Desbordamiento")

    def test_domain_errors(self) -> None:
        self.assert_eval_error("sqrt(-1)", EvaluationError)
        self.assert_eval_error("log(0)", EvaluationError)
        self.assert_eval_error("ln(-2)", EvaluationError)
        self.assert_eval_error("asin(2)", EvaluationError)

    def test_unclosed_paren(self) -> None:
        self.assert_eval_error("(2 + 3", ParserError)

    def test_trailing_garbage(self) -> None:
        self.assert_eval_error("2.5.5", ParserError)
        self.assert_eval_error("5..3", ParserError)

    def test_unknown_identifier(self) -> None:
        self.assert_eval_error("foo(2)", LexerError)
        self.assert_eval_error("banana", LexerError)

    def test_unknown_character(self) -> None:
        self.assert_eval_error("2 @ 3", LexerError)

    def test_error_hierarchy(self) -> None:
        # One except clause catches everything, and each specific error
        # is still distinguishable.
        for expression, cls in [
            ("@", LexerError),
            ("(2", ParserError),
            ("5/0", EvaluationError),
        ]:
            with self.subTest(expression=expression):
                with self.assertRaises(CalculatorError):
                    self.calc.evaluate(expression)
                self.assertTrue(issubclass(cls, CalculatorError))


if __name__ == "__main__":
    unittest.main()
