"""
calculator.py
-------------
Fachada (Facade pattern). Une Lexer -> Parser -> Evaluator en una sola
función pública. La GUI (o cualquier futuro cliente: CLI, API web, tests)
solo necesita conocer esta clase, nunca los detalles internos.

Esto es lo que te permite, a futuro, tener:
    - GUI en JavaScript/Electron llamando a este core por subprocess o API
    - Evaluator reescrito en C++ vía pybind11
sin que el código que USA la calculadora tenga que cambiar una sola línea.
"""

from __future__ import annotations

from .errors import CalculatorError
from .evaluator import ANGLE_DEG, ANGLE_RAD, EvaluationError, Evaluator
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError

# Re-exported so `from .calculator import CalculatorError` keeps working.
# CalculatorError is now a real base class: LexerError, ParserError and
# EvaluationError all subclass it, so `except CalculatorError` catches
# every pipeline failure — and callers can also `raise` or format it.


class Calculator:
    """Facade class that unifies Lexer → Parser → Evaluator into one simple API.

    This is the ONLY class the GUI (or any client) needs to know about.
    It hides the complexity of tokenization, parsing, and evaluation.

    Usage: result = Calculator().evaluate("2 + 3 * 4")  # Returns 14.0

    The beauty of this design: if you swap the Evaluator for a C++ version
    (or add a CLI, or a web API), the code that USES the Calculator doesn't
    need to change at all.
    """

    def __init__(self) -> None:
        self._evaluator = Evaluator()  # Create the evaluator (reused across calls)

    @property
    def angle_mode(self) -> str:
        """'deg' or 'rad' — the unit used by the trigonometric functions."""
        return self._evaluator.angle_mode

    @angle_mode.setter
    def angle_mode(self, mode: str) -> None:
        if mode not in (ANGLE_DEG, ANGLE_RAD):
            raise ValueError(
                f"Modo de ángulo desconocido: {mode!r} (esperado 'deg' o 'rad')"
            )
        self._evaluator.angle_mode = mode

    def evaluate(self, expression: str) -> float:
        """Evaluate a math string and return the result as a float.

        Pipeline: string → tokens → AST → float

        Raises LexerError, ParserError, or EvaluationError if the expression
        is invalid (all catchable together as CalculatorError).
        """
        # Step 1: Tokenize the input string
        tokens = Lexer(expression).tokenize()
        # Step 2: Parse tokens into an Abstract Syntax Tree
        ast = Parser(tokens).parse()
        # Step 3: Evaluate the AST to get the final number
        return self._evaluator.evaluate(ast)
