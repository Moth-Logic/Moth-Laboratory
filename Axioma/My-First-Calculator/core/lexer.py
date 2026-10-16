"""
lexer.py
--------
Responsabilidad única (SRP): convertir un string crudo ("3 + (4 * 2)")
en una lista de Tokens. No sabe nada de precedencia ni de aritmética.

Diseñado para ser reemplazado/extendido sin tocar el resto del sistema:
si mañana agregas potencias (^), módulo (%) o funciones (sin, cos),
el cambio vive aquí y en nada más.
"""

from dataclasses import dataclass
from enum import Enum, auto

from .errors import CalculatorError

# === Token Types ===
# An Enum is a set of named constants. Each token type represents
# what kind of thing the lexer found in the input string.
class TokenType(Enum):
    NUMBER = auto()    # A numeric literal: 3, 3.14, 0.5, etc.
    PLUS = auto()      # The + operator
    MINUS = auto()     # The - operator
    STAR = auto()      # The * operator
    SLASH = auto()     # The / operator
    LPAREN = auto()    # Opening parenthesis (
    RPAREN = auto()    # Closing parenthesis )
    FUNCTION = auto()  # A function name: sin, cos, tan, sqrt, etc.
    COMMA = auto()     # The comma separator in function arguments
    CARET = auto()     # The ^ operator (exponentiation)
    PERCENT = auto()   # The % operator (modulo)
    EOF = auto()       # End of input — no more characters to read


@dataclass(frozen=True)
class Token:
    """A single token produced by the lexer.

    'frozen=True' makes the dataclass immutable — once created,
    a Token can never be modified. This is a safety feature.
    """
    type: TokenType           # What kind of token this is (NUMBER, PLUS, etc.)
    value: float | None = None  # The numeric value (only used for NUMBER tokens)

    def __repr__(self) -> str:
        if self.value is not None:
            return f"Token({self.type.name}, {self.value})"
        return f"Token({self.type.name})"


class LexerError(CalculatorError):
    """Raised when the lexer encounters an unexpected character or a
    malformed numeric literal. Subclasses CalculatorError so callers can
    catch every calculation problem with a single except clause."""


# Map of single characters to their token types.
# This is how the lexer knows that '+' means TokenType.PLUS, etc.
_SINGLE_CHAR_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ",": TokenType.COMMA,
    "^": TokenType.CARET,
    "%": TokenType.PERCENT,
}

# Recognized function names (lowercase). When the lexer sees one of these,
# it creates a FUNCTION token instead of raising an error.
_SCIENTIFIC_FUNCTIONS = frozenset({
    "sin", "cos", "tan",           # Trigonometric (degrees input)
    "asin", "acos", "atan",        # Inverse trig
    "sinh", "cosh", "tanh",        # Hyperbolic
    "sqrt", "cbrt",                 # Roots
    "log", "ln",                    # Logarithms
    "abs", "exp", "ceil", "floor", "round",  # Other math functions
})

# Recognized constant names. When the lexer sees 'pi' or 'e',
# it creates a NUMBER token with the constant's value.
_SCIENTIFIC_CONSTANTS = {
    "pi": 3.141592653589793,
    "e": 2.718281828459045,
}


class Lexer:
    """Converts a raw string expression into a list of Tokens.

    The lexer scans the input character by character and produces tokens.
    It handles: numbers (integers and decimals), operators (+-*/^%),
    parentheses, function names (sin, cos...), and constants (pi, e).

    Usage: tokens = Lexer("3 + sin(45)").tokenize()
    """

    def __init__(self, source: str) -> None:
        self._source = source      # The input string to tokenize
        self._pos = 0             # Current position in the string
        self._length = len(source) # Total length (cached for speed)

    def tokenize(self) -> list[Token]:
        """Scan the entire input and return a list of tokens.

        The last token is always EOF (End Of File), which tells the parser
        that there's nothing left to read.
        """
        tokens: list[Token] = []
        while self._pos < self._length:
            char = self._source[self._pos]

            # Skip whitespace (spaces, tabs, newlines)
            if char.isspace():
                self._pos += 1
                continue

            # If it starts with an ASCII digit or dot, it's a number.
            # (isascii() guard: Unicode digits like '٣' are not valid float
            # literals and must fall through to the error branch below.)
            if (char.isascii() and char.isdigit()) or char == ".":
                tokens.append(self._read_number())
                continue

            # If it starts with a letter or underscore, it's an identifier
            # (could be a function like 'sin' or a constant like 'pi')
            if char.isalpha() or char == "_":
                tokens.append(self._read_identifier())
                continue

            # If it's a known single character (operator, parenthesis, etc.)
            if char in _SINGLE_CHAR_TOKENS:
                tokens.append(Token(_SINGLE_CHAR_TOKENS[char]))
                self._pos += 1
                continue

            # If we get here, the character is not recognized
            raise LexerError(f"Carácter inesperado '{char}' en la posición {self._pos}")

        tokens.append(Token(TokenType.EOF))  # Always end with EOF
        return tokens

    def _read_identifier(self) -> Token:
        """Read a name (letters, digits, underscores) and determine if it's
        a recognized function (sin, cos...) or constant (pi, e).
        If it's neither, raise an error."""
        start = self._pos
        # Keep reading while we have alphanumeric characters or underscores
        while self._pos < self._length and (
            self._source[self._pos].isalnum() or self._source[self._pos] == "_"
        ):
            self._pos += 1
        name = self._source[start:self._pos]  # Extract the full name
        name_lower = name.lower()  # Case-insensitive matching

        # Check if it's a recognized function name
        if name_lower in _SCIENTIFIC_FUNCTIONS:
            return Token(TokenType.FUNCTION, name_lower)

        # Check if it's a recognized constant (pi, e)
        if name_lower in _SCIENTIFIC_CONSTANTS:
            return Token(TokenType.NUMBER, _SCIENTIFIC_CONSTANTS[name_lower])

        # Not a recognized name — this is an error
        raise LexerError(f"Identificador desconocido '{name}' en la posición {start}")

    def _read_number(self) -> Token:
        """Read a numeric literal from the input.

        Handles integers (42), decimals (3.14, .5) and scientific notation
        (1e6, 2.5E-3). Only one dot is allowed ('3.14.5' is rejected).
        The exponent part is only consumed when it is actually followed by
        digits (or a sign + digits), so '2 * e' and 'e' keep working as
        Euler's constant.

        Raises LexerError (never ValueError) for malformed literals such as
        a lone '.' — every input problem must surface as CalculatorError.
        """
        start = self._pos
        seen_dot = False  # Have we already seen a decimal point?

        while self._pos < self._length:
            char = self._source[self._pos]
            if char.isascii() and char.isdigit():
                self._pos += 1
            elif char == "." and not seen_dot:
                seen_dot = True  # First dot found — this is a decimal number
                self._pos += 1
            else:
                break  # Not part of the number anymore

        # Scientific notation: 1e6, 1E+6, 2.5e-3
        if self._pos < self._length and self._source[self._pos] in "eE":
            peek = self._pos + 1
            if peek < self._length and self._source[peek] in "+-":
                peek += 1
            has_exponent = (
                peek < self._length
                and self._source[peek].isascii()
                and self._source[peek].isdigit()
            )
            if has_exponent:
                self._pos = peek
                while self._pos < self._length and (
                    self._source[self._pos].isascii()
                    and self._source[self._pos].isdigit()
                ):
                    self._pos += 1
            # Otherwise: leave the 'e' alone so it can be read as the
            # Euler constant (e.g. "2 * e").

        raw = self._source[start:self._pos]  # Extract the number string
        try:
            value = float(raw)
        except ValueError:
            # e.g. a lone '.' — must not leak a raw ValueError to callers
            raise LexerError(
                f"Número inválido '{raw}' en la posición {start}"
            ) from None
        return Token(TokenType.NUMBER, value)
