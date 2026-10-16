"""
parser.py
---------
Parser recursivo-descendente clásico. Convierte la lista de Tokens en un
AST (Abstract Syntax Tree). Esta es la pieza que hace que "2 + 3 * 4"
se evalúe correctamente como 14 y no como 20, y que "(2 + 3) * 4" respete
los paréntesis.

Gramática (de menor a mayor precedencia):

    expression -> term ( ("+" | "-") term )*
    term       -> factor ( ("*" | "/") factor )*
    power      -> factor ("^" power)?
    factor     -> NUMBER | FUNCTION "(" expression ")" | "(" expression ")" | ("-" | "+") factor

Nota de diseño: el AST (Number, BinaryOp, UnaryOp) es el "contrato" entre
el Parser y el Evaluator. El día que reemplacemos el Evaluator por una
versión en C++ (vía pybind11), este árbol es la estructura de datos que
cruza la frontera Python <-> C++. Por eso vive separado y no mezcla
lógica de evaluación aquí.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from .errors import CalculatorError
from .lexer import Token, TokenType


class ParserError(CalculatorError):
    """Error de sintaxis: paréntesis sin cerrar, token inesperado, etc.

    Subclase de CalculatorError — capturable junto a LexerError y
    EvaluationError con un solo except."""


# ---------------------------------------------------------------------
# Nodos del AST
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class Number:
    value: float


@dataclass(frozen=True)
class BinaryOp:
    left: "ASTNode"
    operator: TokenType
    right: "ASTNode"


@dataclass(frozen=True)
class UnaryOp:
    operator: TokenType
    operand: "ASTNode"


@dataclass(frozen=True)
class FunctionCall:
    name: str
    argument: "ASTNode"


ASTNode = Union[Number, BinaryOp, UnaryOp, FunctionCall]


# ---------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------

class Parser:
    """Converts a list of tokens into an AST (Abstract Syntax Tree).

    Uses recursive descent parsing — each grammar rule becomes a method.
    The parser handles operator precedence automatically through the
    method call hierarchy:

        _expression() handles + and - (lowest precedence)
            _term() handles *, /, % (medium precedence)
                _power() handles ^ (high precedence, right-associative)
                    _factor() handles numbers, functions, parens, unary +/-

    This means '2 + 3 * 4' correctly parses as 2 + (3 * 4) = 14,
    not (2 + 3) * 4 = 20.
    """

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens  # The list of tokens from the lexer
        self._pos = 0          # Current position in the token list

    def parse(self) -> ASTNode:
        """Parse the entire token list and return the root AST node."""
        node = self._expression()
        # After parsing the full expression, we should be at EOF
        if self._current().type != TokenType.EOF:
            raise ParserError(f"Token inesperado al final: {self._current()}")
        return node

    # === expression -> term (('+' | '-') term)* ===
    # Handles addition and subtraction (lowest precedence).
    # Left-associative: '1+2+3' = (1+2)+3, not 1+(2+3).
    def _expression(self) -> ASTNode:
        node = self._term()  # Start with the highest-precedence sub-expression
        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self._advance().type  # Consume the operator
            node = BinaryOp(node, op, self._term())  # Build a tree node
        return node

    # === term -> power (('*' | '/' | '%') power)* ===
    # Handles multiplication, division, and modulo (medium precedence).
    def _term(self) -> ASTNode:
        node = self._power()
        while self._current().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._advance().type
            node = BinaryOp(node, op, self._power())
        return node

    # === power -> factor ('^' power)? ===
    # Handles exponentiation (high precedence, RIGHT-associative).
    # Right-associative means '2^3^2' = 2^(3^2) = 2^9 = 512, not (2^3)^2 = 64.
    def _power(self) -> ASTNode:
        node = self._factor()
        if self._current().type == TokenType.CARET:
            self._advance()  # Consume '^'
            node = BinaryOp(node, TokenType.CARET, self._power())  # Recursive call = right-associative
        return node

    # === factor -> NUMBER | FUNCTION '(' expr ')' | '(' expr ')' | ('-' | '+') factor ===
    # The highest-precedence rule: handles atoms (numbers, constants, functions)
    # and grouping with parentheses.
    def _factor(self) -> ASTNode:
        token = self._current()

        # Unary +/-: e.g., -5 or +3
        if token.type in (TokenType.PLUS, TokenType.MINUS):
            self._advance()  # Consume the sign
            return UnaryOp(token.type, self._factor())  # Recursive: allows --5, +-3, etc.

        # Number literal: 42, 3.14, etc.
        if token.type == TokenType.NUMBER:
            self._advance()
            return Number(token.value)  # type: ignore[arg-type]

        # Function call: sin(45), sqrt(16), etc.
        if token.type == TokenType.FUNCTION:
            func_name = token.value  # type: ignore[assignment]
            self._advance()
            self._expect(TokenType.LPAREN, f"Se esperaba '(' después de {func_name}")
            argument = self._expression()  # Parse the argument (can be any expression)
            self._expect(TokenType.RPAREN, f"Se esperaba ')' después del argumento de {func_name}")
            return FunctionCall(func_name, argument)  # type: ignore[arg-type]

        # Parenthesized expression: (2 + 3) * 4
        if token.type == TokenType.LPAREN:
            self._advance()  # Consume '('
            node = self._expression()  # Parse whatever is inside
            self._expect(TokenType.RPAREN, "Se esperaba ')'")  # Consume ')'
            return node  # Return the inner expression (the parens just group it)

        raise ParserError(f"Token inesperado: {token}")

    # === Helper methods ===

    def _current(self) -> Token:
        """Look at the current token without consuming it."""
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        """Consume and return the current token, moving to the next one."""
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def _expect(self, type_: TokenType, message: str) -> Token:
        """Consume the current token only if it matches the expected type.

        If it doesn't match, raise a ParserError with a helpful message.
        """
        if self._current().type != type_:
            raise ParserError(f"{message} (encontrado: {self._current()})")
        return self._advance()
