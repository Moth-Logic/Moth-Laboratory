"""
Axioma Language Lexer
=====================
Manual character-by-character lexer for the Axioma programming language.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


# ── Token Types ───────────────────────────────────────────────────────────────

class TT(Enum):
    # Literals
    INTEGER     = auto()   # 42
    REAL        = auto()   # 3.14
    STRING      = auto()   # "hello" or s"hello {var}"
    BOOL        = auto()   # T / F
    NULL        = auto()   # Null

    # Identifiers & Keywords
    IDENT       = auto()   # variable / function names
    KEYWORD     = auto()   # reserved words

    # Math set literals
    MATHSET     = auto()   # NN ZZ QQ II RR CC ii

    # Operators — arithmetic
    PLUS        = auto()   # +
    MINUS       = auto()   # -
    STAR        = auto()   # *
    SLASH       = auto()   # /
    DOUBLESLASH = auto()   # //
    PERCENT     = auto()   # %
    STARSTAR    = auto()   # **

    # Operators — comparison
    EQ          = auto()   # ===
    NEQ         = auto()   # =!=
    LT          = auto()   # <
    GT          = auto()   # >
    LTE         = auto()   # <=
    GTE         = auto()   # >=

    # Operators — assignment
    ASSIGN      = auto()   # :=
    PLUSEQ      = auto()   # +=
    MINUSEQ     = auto()   # -=
    STAREQ      = auto()   # *=
    SLASHEQ     = auto()   # /=
    DOMAIN      = auto()   # ::  (type domain declaration)

    # Operators — logical
    AND         = auto()   # &&
    OR          = auto()   # ||
    NOT         = auto()   # !!

    # Operators — bitwise
    AMPERSAND   = auto()   # &
    PIPE        = auto()   # |
    CARET       = auto()   # ^
    TILDE       = auto()   # ~
    LSHIFT      = auto()   # <<
    RSHIFT      = auto()   # >>

    # Operators — special
    HASH        = auto()   # #  (length)
    PRIME       = auto()   # '  (projection / attribute access)
    AT          = auto()   # @
    DCOLON      = auto()   # :: (decorator / transformation)
    ARROW       = auto()   # ->
    FATARROW    = auto()   # =>
    QUESTION    = auto()   # ?  (ternary)
    COLON       = auto()   # :  (type hint)
    DOTDOT      = auto()   # .. (range)
    ELLIPSIS    = auto()   # ... (varargs / infinity)
    PIPE_COMP   = auto()   # |  used in comprehensions (shared with PIPE)

    # Delimiters
    LPAREN      = auto()   # (
    RPAREN      = auto()   # )
    LBRACKET    = auto()   # [
    RBRACKET    = auto()   # ]
    LBRACE      = auto()   # {
    RBRACE      = auto()   # }
    LANGLE      = auto()   # ⟨  (generator comprehension)
    RANGLE      = auto()   # ⟩

    # Separators
    COMMA       = auto()   # ,
    SEMICOLON   = auto()   # ;
    NEWLINE     = auto()   # \n (statement separator)

    # Special
    COMMENT     = auto()   # -- ...
    UNDERSCORE  = auto()   # _ (used in S_{i} subscript notation)
    EOF         = auto()


# ── Keywords ──────────────────────────────────────────────────────────────────

KEYWORDS = {
    # Control flow
    "let", "given", "otherwise",
    "each", "repeat", "until", "in",
    "stop", "next", "skip",
    # Functions
    "where", "fn", "report",
    # OOP
    "structure", "extends", "create", "this", "parent",
    "static", "property", "fixed", "immutable",
    # Error handling
    "check", "catch", "resolve", "always", "abort", "cause", "fallback",
    # Modules
    "using", "from", "provide", "as", "export", "if", "main",
    # Async
    "spawn", "collect",
    # Generators
    "emit", "expand",
    # Variables / scope
    "outer", "scope", "drop", "verify",
    # Context managers
    "assume", "on_open", "on_close",
    # Math operators (word form)
    "union", "intersect", "exclude", "cart",
    "deriv", "integ", "sum", "prod", "nrt",
    "by",       # used in slicing: a[1..3 by 2]
    "begin", "end",
    # Pattern matching
    "case",
    # Built-ins (word form)
    "out", "type", "is", "inherits",
    "Sequence", "Tuple", "Mapping", "Set", "FrozenSet",
    "ConstantSet", "Binary", "MutableBinary",
    "ZZ", "RR", "CC", "NN", "QQ", "II", "ii",
    "Bool", "CharSequence", "Null",
    "sup", "inf", "round", "sort", "reverse",
    "apply", "select", "fold", "specialize",
    "stream", "load", "store",
    "exists", "identity", "hash",
    "scope", "inspect", "doc",
    "compute", "run", "get", "set",
    "base", "entity", "method",
    "sequence", "is_function",
    "stringify", "format",
    "char", "code",
    "base2", "base8", "base16",
    "indexed", "combine",
    "LexicalContext",
}

# Math sets: treated as keywords but grouped separately for clarity
MATH_SETS = {"NN", "ZZ", "QQ", "II", "RR", "ii", "CC"}

# Boolean / Null literals
BOOL_LITERALS = {"T", "F"}
NULL_LITERAL  = "Null"

# Canonical Axioma source file extension.
SOURCE_EXTENSION = ".axm"

# Single-character token table — built once at import time instead of on
# every call to _scan_token() (was previously a fresh dict literal per token).
_SINGLE_CHAR_TOKENS = {
    "(": TT.LPAREN,  ")": TT.RPAREN,
    "[": TT.LBRACKET,"]": TT.RBRACKET,
    "{": TT.LBRACE,  "}": TT.RBRACE,
    ",": TT.COMMA,   ";": TT.SEMICOLON,
    "#": TT.HASH,    "'": TT.PRIME,
    "@": TT.AT,      "?": TT.QUESTION,
    "^": TT.CARET,   "~": TT.TILDE,
    "%": TT.PERCENT, "_": TT.UNDERSCORE,
}


# ── Token dataclass ───────────────────────────────────────────────────────────

@dataclass
class Token:
    type:   TT
    value:  object          # raw value (string, int, float, etc.)
    line:   int
    col:    int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


# ── Lexer Error ───────────────────────────────────────────────────────────────

class LexerError(Exception):
    def __init__(self, msg: str, line: int, col: int):
        super().__init__(f"[Lexer] {msg} at line {line}, col {col}")
        self.line = line
        self.col  = col


# ── Lexer ─────────────────────────────────────────────────────────────────────

class Lexer:
    def __init__(self, source: str):
        self.src    = source
        self.pos    = 0
        self.line   = 1
        self.col    = 1
        self.tokens: List[Token] = []

    # ── Helpers ───────────────────────────────────────────────────────────────

    def current(self) -> Optional[str]:
        """Return current character, or None at EOF."""
        return self.src[self.pos] if self.pos < len(self.src) else None

    def peek(self, offset: int = 1) -> Optional[str]:
        """Peek ahead without advancing."""
        idx = self.pos + offset
        return self.src[idx] if idx < len(self.src) else None

    def advance(self) -> str:
        """Consume current character and return it."""
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def match(self, expected: str) -> bool:
        """Consume the next character only if it matches expected."""
        if self.current() == expected:
            self.advance()
            return True
        return False

    def add(self, tt: TT, value: object, line: int, col: int):
        self.tokens.append(Token(tt, value, line, col))

    def here(self):
        """Snapshot current line/col (before advancing)."""
        return self.line, self.col

    # ── Main tokenize loop ────────────────────────────────────────────────────

    def tokenize(self) -> List[Token]:
        while self.current() is not None:
            self._scan_token()
        self.add(TT.EOF, None, self.line, self.col)
        return self.tokens

    def _scan_token(self):
        line, col = self.here()
        ch = self.advance()

        # ── Whitespace (skip, but preserve newlines) ──────────────────────────
        if ch in (" ", "\t", "\r"):
            return
        if ch == "\n":
            # Collapse multiple blank lines into one NEWLINE token
            if not self.tokens or self.tokens[-1].type != TT.NEWLINE:
                self.add(TT.NEWLINE, "\n", line, col)
            return

        # ── Comments: -- / arrow: -> / minus / -= ──────────────────────────────
        if ch == "-":
            if self.current() == "-":
                self.advance()                      # consume second -
                text = self._read_until_newline()
                self.add(TT.COMMENT, text.strip(), line, col)
                return
            # BUGFIX: '->' must be checked here, before falling back to
            # MINUS/-=. It previously lived in unreachable code further
            # down this function (this whole `ch == "-"` branch always
            # returns), so ARROW was never emitted and every lambda
            # `(x) -> expr` failed to parse.
            if self.match(">"):
                self.add(TT.ARROW, "->", line, col)
            elif self.match("="):
                self.add(TT.MINUSEQ, "-=", line, col)
            else:
                self.add(TT.MINUS, "-", line, col)
            return

        # ── String literals ───────────────────────────────────────────────────
        if ch == '"':
            self.add(TT.STRING, self._read_string(interpolated=False), line, col)
            return
        if ch == "s" and self.current() == '"':
            self.advance()   # consume opening "
            self.add(TT.STRING, self._read_string(interpolated=True), line, col)
            return

        # ── Numbers ───────────────────────────────────────────────────────────
        if ch.isdigit():
            self.add(*self._read_number(ch, line, col))
            return

        # ── Identifiers & keywords ────────────────────────────────────────────
        if ch.isalpha() or ch == "_":
            ident = ch + self._read_while(lambda c: c.isalnum() or c == "_")
            self._emit_ident_or_keyword(ident, line, col)
            return

        # ── Unicode: ⟨ ⟩ (generator comprehension delimiters) ────────────────
        if ch == "\u27e8":   # ⟨
            self.add(TT.LANGLE, "⟨", line, col)
            return
        if ch == "\u27e9":   # ⟩
            self.add(TT.RANGLE, "⟩", line, col)
            return

        # ── Multi-character operators ─────────────────────────────────────────
        if ch == ":":
            if self.match(":"):
                self.add(TT.DOMAIN, "::", line, col)
            elif self.match("="):
                self.add(TT.ASSIGN, ":=", line, col)
            else:
                self.add(TT.COLON, ":", line, col)
            return

        if ch == "=":
            if self.current() == "=" and self.peek(1) == "=":
                self.advance(); self.advance()
                self.add(TT.EQ, "===", line, col)
            elif self.current() == "!" and self.peek(1) == "=":
                self.advance(); self.advance()
                self.add(TT.NEQ, "=!=", line, col)
            elif self.match(">"):
                self.add(TT.FATARROW, "=>", line, col)
            else:
                raise LexerError(f"Unexpected '=' (did you mean ':=' or '==='?)", line, col)
            return

        if ch == "!":
            if self.match("!"):
                self.add(TT.NOT, "!!", line, col)
            else:
                raise LexerError("Single '!' is not valid — use '!!' for NOT", line, col)
            return

        if ch == "&":
            if self.match("&"):
                self.add(TT.AND, "&&", line, col)
            else:
                self.add(TT.AMPERSAND, "&", line, col)
            return

        if ch == "|":
            if self.match("|"):
                self.add(TT.OR, "||", line, col)
            else:
                self.add(TT.PIPE, "|", line, col)
            return

        if ch == "<":
            if self.match("<"):
                self.add(TT.LSHIFT, "<<", line, col)
            elif self.match("="):
                self.add(TT.LTE, "<=", line, col)
            else:
                self.add(TT.LT, "<", line, col)
            return

        if ch == ">":
            if self.match(">"):
                self.add(TT.RSHIFT, ">>", line, col)
            elif self.match("="):
                self.add(TT.GTE, ">=", line, col)
            else:
                self.add(TT.GT, ">", line, col)
            return

        if ch == ".":
            if self.current() == "." and self.peek(1) == ".":
                self.advance(); self.advance()
                self.add(TT.ELLIPSIS, "...", line, col)
            elif self.match("."):
                self.add(TT.DOTDOT, "..", line, col)
            else:
                raise LexerError("Lone '.' is not valid in Axioma", line, col)
            return

        if ch == "*":
            if self.match("*"):
                self.add(TT.STARSTAR, "**", line, col)
            elif self.match("="):
                self.add(TT.STAREQ, "*=", line, col)
            else:
                self.add(TT.STAR, "*", line, col)
            return

        if ch == "/":
            if self.match("/"):
                self.add(TT.DOUBLESLASH, "//", line, col)
            elif self.match("="):
                self.add(TT.SLASHEQ, "/=", line, col)
            else:
                self.add(TT.SLASH, "/", line, col)
            return

        if ch == "+":
            if self.match("="):
                self.add(TT.PLUSEQ, "+=", line, col)
            else:
                self.add(TT.PLUS, "+", line, col)
            return

        # ── Single-character tokens ───────────────────────────────────────────
        if ch in _SINGLE_CHAR_TOKENS:
            self.add(_SINGLE_CHAR_TOKENS[ch], ch, line, col)
            return

        raise LexerError(f"Unexpected character {ch!r}", line, col)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _read_while(self, condition) -> str:
        result = []
        while self.current() is not None and condition(self.current()):
            result.append(self.advance())
        return "".join(result)

    def _read_until_newline(self) -> str:
        return self._read_while(lambda c: c != "\n")

    def _read_string(self, interpolated: bool) -> "str | tuple[str, str]":
        """Read characters until closing quote, handling escape sequences."""
        result = []
        while True:
            ch = self.current()
            if ch is None:
                raise LexerError("Unterminated string", self.line, self.col)
            if ch == '"':
                self.advance()
                break
            if ch == "\\":
                self.advance()
                esc = self.advance()
                result.append({"n": "\n", "t": "\t", "\\": "\\", '"': '"'}.get(esc, esc))
            else:
                result.append(self.advance())
        raw = "".join(result)
        # Mark interpolated strings so the parser knows to handle {var}
        return ("s:", raw) if interpolated else raw

    def _read_number(self, first: str, line: int, col: int):
        """Read an integer or real number."""
        digits = first + self._read_while(lambda c: c.isdigit() or c == "_")
        digits = digits.replace("_", "")   # allow 1_000_000 style
        if self.current() == "." and self.peek() != ".":
            self.advance()
            frac = self._read_while(str.isdigit)
            return TT.REAL, float(f"{digits}.{frac}"), line, col
        return TT.INTEGER, int(digits), line, col

    def _emit_ident_or_keyword(self, word: str, line: int, col: int):
        if word == NULL_LITERAL:
            self.add(TT.NULL, None, line, col)
        elif word in BOOL_LITERALS:
            self.add(TT.BOOL, word == "T", line, col)
        elif word in MATH_SETS:
            self.add(TT.MATHSET, word, line, col)
        elif word in KEYWORDS:
            self.add(TT.KEYWORD, word, line, col)
        else:
            self.add(TT.IDENT, word, line, col)


# ── Pretty printer ────────────────────────────────────────────────────────────

def print_tokens(tokens: List[Token]):
    for tok in tokens:
        if tok.type == TT.COMMENT:
            print(f"  {tok.line:>3}:{tok.col:<3} COMMENT       -- {tok.value}")
        elif tok.type == TT.NEWLINE:
            print(f"  {tok.line:>3}:{tok.col:<3} NEWLINE")
        elif tok.type == TT.EOF:
            print(f"  {tok.line:>3}:{tok.col:<3} EOF")
        else:
            print(f"  {tok.line:>3}:{tok.col:<3} {tok.type.name:<14} {tok.value!r}")


# ── Test driver ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = r"""
-- A simple Axioma program

where greet(name : CharSequence) : CharSequence begin
  report s"Hello, {name}!"
end

let nums :: Sequence
let nums := [1, 2, 3, 4, 5]

each n in nums begin
  let n % 2 === 0 begin
    out(n)
  end
end

let squares := [x ** 2 | x in {1..10}]

let active : Bool := T
let nothing : Null := Null
let big := 1_000_000

-- Math sets
let integers :: ZZ
let reals :: RR

verify #nums === 5
"""

    print("═" * 50)
    print("  AXIOMA LEXER — Token Stream")
    print("═" * 50)
    lexer  = Lexer(sample)
    tokens = lexer.tokenize()
    print_tokens(tokens)
    print("═" * 50)
    print(f"  Total tokens: {len(tokens)}")
