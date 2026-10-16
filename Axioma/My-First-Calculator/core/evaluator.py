"""
evaluator.py
------------
Recorre el AST (patrón Visitor simplificado) y produce el número final.

Este módulo intenta usar la implementación C++ (_evaluator_cpp) para
obtener máximo rendimiento. Si el módulo C++ no está compilado, cae
graciosamente al evaluator puro en Python (graceful degradation).

El backend C++ tiene las funciones trigonométricas en grados
hardcodeadas, así que solo se usa cuando el modo de ángulo es 'deg';
en modo 'rad' (o sin .pyd compilado) se usa el camino Python.

Sea cual sea el backend, el resultado se valida al final: cualquier
resultado no finito (infinito o NaN) se convierte en EvaluationError
en vez de escapar como OverflowError/ValueError al GUI.
"""

from __future__ import annotations

import math
from typing import Callable

from .errors import CalculatorError
from .lexer import TokenType
from .parser import ASTNode, BinaryOp, FunctionCall, Number, UnaryOp

# === C++ Backend (optional performance optimization) ===
# If the C++ extension module is compiled, we use it for faster evaluation.
# If not, we fall back to pure Python (graceful degradation).
try:
    from ._evaluator_cpp import evaluate as _cpp_evaluate
    _HAS_CPP = True  # C++ backend available — use it!
except ImportError:
    _HAS_CPP = False  # No C++ module — use pure Python instead


class EvaluationError(CalculatorError):
    """Raised when evaluation fails (division by zero, unknown node, etc.).

    Subclasses CalculatorError so callers can catch every calculation
    problem with a single except clause.
    """


# === Angle modes for the trigonometric functions ===
ANGLE_DEG = "deg"
ANGLE_RAD = "rad"
ANGLE_MODES = (ANGLE_DEG, ANGLE_RAD)


def _build_functions(angle_mode: str) -> dict[str, Callable[[float], float]]:
    """Build the name -> callable map for the given angle mode.

    Only the six trigonometric functions depend on the angle mode:
    in 'deg' mode inputs are converted to radians internally (and the
    inverse functions convert their result back to degrees); in 'rad'
    mode values are used as-is.
    """
    if angle_mode == ANGLE_DEG:
        trig: dict[str, Callable[[float], float]] = {
            "sin": lambda x: math.sin(math.radians(x)),
            "cos": lambda x: math.cos(math.radians(x)),
            "tan": lambda x: math.tan(math.radians(x)),
            "asin": lambda x: math.degrees(math.asin(x)),
            "acos": lambda x: math.degrees(math.acos(x)),
            "atan": lambda x: math.degrees(math.atan(x)),
        }
    else:  # ANGLE_RAD
        trig = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
        }

    functions: dict[str, Callable[[float], float]] = dict(trig)
    functions.update({
        # Hyperbolic functions (always radians)
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        # Power and roots
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),  # Preserves sign for negatives
        "exp": math.exp,
        # Logarithms
        "log": math.log10,   # log base 10
        "ln": math.log,      # natural log (base e)
        # Rounding
        "ceil": math.ceil,
        "floor": math.floor,
        "round": round,
        # Other
        "abs": abs,
    })
    return functions


class Evaluator:
    """Walks the AST and produces the final number.

    Args:
        angle_mode: 'deg' (default) or 'rad' — how the trigonometric
            functions interpret their arguments.
    """

    def __init__(self, angle_mode: str = ANGLE_DEG) -> None:
        self._angle_mode = ANGLE_DEG
        self.angle_mode = angle_mode  # validates and builds the function table
        self._functions = _build_functions(self._angle_mode)

    # --- Angle mode -------------------------------------------------------

    @property
    def angle_mode(self) -> str:
        """'deg' or 'rad' — the unit used by the trig functions."""
        return self._angle_mode

    @angle_mode.setter
    def angle_mode(self, mode: str) -> None:
        if mode not in ANGLE_MODES:
            raise ValueError(
                f"Modo de ángulo desconocido: {mode!r} (esperado 'deg' o 'rad')"
            )
        self._angle_mode = mode
        self._functions = _build_functions(mode)

    # --- Public API -------------------------------------------------------

    def evaluate(self, node: ASTNode) -> float:
        """Walk the AST recursively and compute the final numeric result.

        Picks the backend exactly once for the whole tree:
          - C++ when the extension is compiled AND the angle mode is 'deg'
            (the C++ side hardcodes degrees).
          - Pure Python otherwise.

        The result is then validated: non-finite results (inf / NaN) raise
        EvaluationError instead of leaking into the GUI.
        """
        if _HAS_CPP and self._angle_mode == ANGLE_DEG:
            try:
                result = float(_cpp_evaluate(node))
            except ValueError as exc:
                raise EvaluationError(str(exc)) from exc
        else:
            result = self._eval_py(node)

        if isinstance(result, complex):
            raise EvaluationError(
                "Resultado complejo no soportado (base negativa con exponente fraccionario)"
            )
        if not math.isfinite(result):
            raise EvaluationError("Resultado demasiado grande (infinito o NaN)")
        return result

    # --- Pure Python fallback --------------------------------------------

    def _eval_py(self, node: ASTNode) -> float:
        """Evaluate an AST node in pure Python (no C++ delegation).

        Each node type has its own handling:
        - Number: just return its value
        - UnaryOp: negate the operand (for -5, +3, etc.)
        - BinaryOp: evaluate both sides and apply the operator
        - FunctionCall: evaluate the argument, then apply the function
        """
        if isinstance(node, Number):
            return node.value  # Base case: numbers just return their value

        if isinstance(node, UnaryOp):
            value = self._eval_py(node.operand)  # Recursively evaluate the operand
            return -value if node.operator == TokenType.MINUS else value

        if isinstance(node, BinaryOp):
            left = self._eval_py(node.left)    # Evaluate the left side
            right = self._eval_py(node.right)  # Evaluate the right side
            return self._apply(node.operator, left, right)  # Apply the operator

        if isinstance(node, FunctionCall):
            return self._apply_function(node)

        raise EvaluationError(f"Nodo AST desconocido: {node!r}")

    def _apply_function(self, node: FunctionCall) -> float:
        """Evaluate a scientific function on an AST node.

        Looks up the function name in the current angle-mode table,
        evaluates the argument, and applies the function. Every math
        error (domain, overflow, division by zero) is normalized to
        EvaluationError so callers only ever see CalculatorError.
        """
        value = self._eval_py(node.argument)
        func = self._functions.get(node.name)
        if func is None:
            raise EvaluationError(f"Función desconocida: {node.name}")
        try:
            result = func(value)
        except ValueError as exc:
            raise EvaluationError(f"Error en {node.name}({value}): {exc}") from exc
        except ZeroDivisionError as exc:
            raise EvaluationError(f"División por cero en {node.name}({value})") from exc
        except OverflowError as exc:
            # e.g. exp(1000) — "math range error"
            raise EvaluationError(
                f"Desbordamiento en {node.name}({value}): resultado demasiado grande"
            ) from exc
        except TypeError as exc:
            raise EvaluationError(f"Error en {node.name}({value}): {exc}") from exc
        return result

    @staticmethod
    def _apply(operator: TokenType, left: float, right: float) -> float:
        """Apply a binary operator to two numbers and return the result.

        Handles: +, -, *, /, ^ (power), % (modulo).
        Raises EvaluationError for division by zero or unknown operators.
        Non-finite results (e.g. 1e308 * 10) are caught later, once, by
        evaluate()'s finiteness check.
        """
        if operator == TokenType.PLUS:
            return left + right
        if operator == TokenType.MINUS:
            return left - right
        if operator == TokenType.STAR:
            return left * right
        if operator == TokenType.SLASH:
            if right == 0:
                raise EvaluationError("División entre cero")
            return left / right
        if operator == TokenType.CARET:
            try:
                result = left ** right
            except OverflowError:
                raise EvaluationError("Resultado demasiado grande")  # e.g., 999^999
            except (ValueError, ZeroDivisionError) as exc:
                raise EvaluationError(f"Potencia inválida: {exc}") from exc
            return result
        if operator == TokenType.PERCENT:
            if right == 0:
                raise EvaluationError("Módulo por cero")
            return left % right
        raise EvaluationError(f"Operador desconocido: {operator}")
