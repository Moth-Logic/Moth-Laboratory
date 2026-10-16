"""
Axioma Language Parser
======================
Recursive descent parser. Takes the token stream from the lexer
and builds an AST (Abstract Syntax Tree).

Usage:
    from lexer import Lexer
    from parser import Parser

    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens).parse()
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any
from axioma_lexer import Lexer, Token, TT # type: ignore


# ══════════════════════════════════════════════════════════════════════════════
#  AST Node definitions
#  Every node is a dataclass so it's easy to inspect / pretty-print.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Node:
    """Base class for all AST nodes."""
    pass


# ── Statements ────────────────────────────────────────────────────────────────

@dataclass
class Program(Node):
    body: List[Node]

@dataclass
class Block(Node):
    stmts: List[Node]

@dataclass
class VarDecl(Node):
    """let x : Type := expr   |   let x :: Type"""
    name:      str
    type_hint: Optional[str]   # after  :
    domain:    Optional[str]   # after ::
    value:     Optional[Node]  # after :=

@dataclass
class FuncDef(Node):
    """where f(params) : ReturnType begin ... end"""
    name:        str
    params:      List[Param]
    return_type: Optional[str]
    body:        Block
    is_spawn:    bool = False   # spawn where ...

@dataclass
class Param(Node):
    name:      str
    type_hint: Optional[str]
    variadic:  bool = False    # ...args

@dataclass
class ReturnStmt(Node):
    """report expr"""
    value: Node

@dataclass
class IfStmt(Node):
    """let cond begin ... end given cond begin ... end otherwise begin ... end"""
    branches:  List[tuple]     # list of (condition, Block)
    otherwise: Optional[Block]

@dataclass
class EachStmt(Node):
    """each x in expr begin ... end"""
    var:  str
    iter: Node
    body: Block

@dataclass
class RepeatStmt(Node):
    """repeat begin ... end until cond"""
    body:      Block
    condition: Node

@dataclass
class MatchStmt(Node):
    """given expr: | case val -> ... | otherwise -> ..."""
    subject:  Node
    cases:    List[tuple]      # list of (value_expr, Block)
    default:  Optional[Block]

@dataclass
class CheckStmt(Node):
    """check / catch / resolve / always"""
    body:     Block
    catches:  List[CatchClause]
    resolve:  Optional[Block]
    always:   Optional[Block]

@dataclass
class CatchClause(Node):
    error_type: Optional[str]
    alias:      Optional[str]
    body:       Block

@dataclass
class AbortStmt(Node):
    """abort expr   |   abort expr cause expr"""
    value: Node
    cause: Optional[Node]

@dataclass
class UsingStmt(Node):
    """using module   |   using module as alias"""
    module: str
    alias:  Optional[str]

@dataclass
class FromStmt(Node):
    """from module provide x, y"""
    module:  str
    names:   List[str]

@dataclass
class StructDef(Node):
    """structure Name := ... end   |   structure Name extends Base := ... end"""
    name:      str
    base:      Optional[str]
    immutable: bool
    members:   List[Node]

@dataclass
class StructField(Node):
    name:      str
    type_hint: Optional[str]
    default:   Optional[Node] = None
    is_static: bool = False
    immutable: bool = False   # `fixed` / `immutable` field modifier

@dataclass
class ExprStmt(Node):
    """A bare expression used as a statement."""
    expr: Node

@dataclass
class SkipStmt(Node):
    """skip (pass)"""
    pass

@dataclass
class StopStmt(Node):
    """stop (break)"""
    pass

@dataclass
class NextStmt(Node):
    """next (continue)"""
    pass

@dataclass
class DropStmt(Node):
    """drop x"""
    name: str

@dataclass
class VerifyStmt(Node):
    """verify expr"""
    expr: Node

@dataclass
class EmitStmt(Node):
    """emit expr"""
    value: Node

@dataclass
class ExpandStmt(Node):
    """expand expr"""
    value: Node

@dataclass
class UsingAsStmt(Node):
    """using expr as name begin ... end  (context manager)"""
    expr:  Node
    alias: str
    body:  Block

@dataclass
class IfMain(Node):
    """if main: begin ... end"""
    body: Block

# ── Expressions ───────────────────────────────────────────────────────────────

@dataclass
class Literal(Node):
    value: Any                 # int, float, str, bool, None

@dataclass
class InterpolatedString(Node):
    """s"Hello, {name}!" """
    raw: str                   # the raw string with {var} placeholders

@dataclass
class Identifier(Node):
    name: str

@dataclass
class MathSet(Node):
    """NN ZZ QQ II RR CC ii"""
    name: str

@dataclass
class BinaryOp(Node):
    op:    str
    left:  Node
    right: Node

@dataclass
class UnaryOp(Node):
    op:      str
    operand: Node

@dataclass
class LenOp(Node):
    """#expr"""
    operand: Node

@dataclass
class Call(Node):
    """f(args)"""
    callee: Node
    args:   List[Node]

@dataclass
class Projection(Node):
    """obj'field"""
    obj:   Node
    field: str

@dataclass
class Subscript(Node):
    """S_{i}  →  parsed as S[i]"""
    obj:   Node
    index: Node

@dataclass
class Slice(Node):
    """a[1..3 by 2]"""
    obj:   Node
    start: Node
    stop:  Node
    step:  Optional[Node]

@dataclass
class Range(Node):
    """{1..10}"""
    start: Node
    stop:  Node

@dataclass
class Ternary(Node):
    """cond ? then_expr : else_expr"""
    condition:  Node
    then_expr:  Node
    else_expr:  Node

@dataclass
class LambdaExpr(Node):
    """fn(params) => expr"""
    params: List[Param]
    body:   Node

@dataclass
class ListExpr(Node):
    """[a, b, c]"""
    elements: List[Node]

@dataclass
class SetExpr(Node):
    """{a, b, c}"""
    elements: List[Node]

@dataclass
class MappingExpr(Node):
    """{key: val, ...}"""
    pairs: List[tuple]         # list of (key_expr, value_expr)

@dataclass
class ListComp(Node):
    """[expr | var in iter, ...conditions]"""
    expr:       Node
    var:        str
    iter:       Node
    conditions: List[Node]

@dataclass
class SetComp(Node):
    """{expr | var in iter}"""
    expr:       Node
    var:        str
    iter:       Node
    conditions: List[Node]

@dataclass
class MappingComp(Node):
    """{key : val | (k, v) in iter}"""
    key_expr: Node
    val_expr: Node
    var:      str
    iter:     Node

@dataclass
class GeneratorComp(Node):
    """⟨expr | var in iter⟩"""
    expr: Node
    var:  str
    iter: Node

@dataclass
class Unpack(Node):
    """{a, b} := {1, 2}  or  ...rest"""
    names:   List[str]
    rest:    Optional[str]     # name after ...

@dataclass
class Assign(Node):
    """name :=  or  name op= expr"""
    target: Node
    op:     str                # ':=' | '+=' | '-=' | '*=' | '/='
    value:  Node

@dataclass
class CollectExpr(Node):
    """collect expr"""
    value: Node

@dataclass
class SpawnExpr(Node):
    """spawn expr"""
    value: Node


# ══════════════════════════════════════════════════════════════════════════════
#  Parser Error
# ══════════════════════════════════════════════════════════════════════════════

class ParseError(Exception):
    def __init__(self, msg: str, tok: Token):
        super().__init__(f"[Parser] {msg} — got {tok.type.name}({tok.value!r}) at {tok.line}:{tok.col}")
        self.token = tok


# ══════════════════════════════════════════════════════════════════════════════
#  Parser
# ══════════════════════════════════════════════════════════════════════════════

class Parser:
    def __init__(self, tokens: List[Token]):
        # Strip comments; keep NEWLINEs as statement separators
        self.tokens = [t for t in tokens if t.type != TT.COMMENT]
        self.pos    = 0

    # ── Primitives ────────────────────────────────────────────────────────────

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def check(self, tt: TT, value: Any = None) -> bool:
        t = self.current()
        if t.type != tt:
            return False
        return value is None or t.value == value

    def match(self, tt: TT, value: Any = None) -> Optional[Token]:
        if self.check(tt, value):
            return self.advance()
        return None

    def expect(self, tt: TT, value: Any = None) -> Token:
        if self.check(tt, value):
            return self.advance()
        hint = f"'{value}'" if value else tt.name
        raise ParseError(f"Expected {hint}", self.current())

    def skip_newlines(self):
        while self.check(TT.NEWLINE):
            self.advance()

    def is_kw(self, *words) -> bool:
        t = self.current()
        return t.type == TT.KEYWORD and t.value in words

    def expect_kw(self, word: str) -> Token:
        if self.is_kw(word):
            return self.advance()
        raise ParseError(f"Expected keyword '{word}'", self.current())

    # ── Entry point ───────────────────────────────────────────────────────────

    def parse(self) -> Program:
        stmts = []
        self.skip_newlines()
        while not self.check(TT.EOF):
            stmts.append(self.parse_stmt())
            self.skip_newlines()
        return Program(stmts)

    # ── Statements ────────────────────────────────────────────────────────────

    def parse_stmt(self) -> Node:
        # Tag every top-level statement node with the line/col it started
        # on. This is a lightweight, non-dataclass attribute (no schema
        # change needed on ~40 Node subclasses) that the interpreter uses
        # to report accurate line numbers on runtime errors.
        start_tok = self.current()
        node = self._parse_stmt_inner()
        if not hasattr(node, "line"):
            node.line = start_tok.line
            node.col  = start_tok.col
        return node

    def _parse_stmt_inner(self) -> Node:
        t = self.current()

        # keyword-dispatched statements
        if t.type == TT.KEYWORD:
            v = t.value
            if v == "let":       return self.parse_var_decl()
            if v == "where":     return self.parse_func_def()
            if v == "spawn":     return self.parse_spawn_stmt()
            if v == "report":    return self.parse_return()
            if v == "each":      return self.parse_each()
            if v == "repeat":    return self.parse_repeat()
            if v == "given":     return self.parse_match()
            if v == "check":     return self.parse_check()
            if v == "abort":     return self.parse_abort()
            if v == "using":     return self.parse_using()
            if v == "from":      return self.parse_from()
            if v == "structure": return self.parse_structure()
            if v == "skip":      self.advance(); return SkipStmt()
            if v == "stop":      self.advance(); return StopStmt()
            if v == "next":      self.advance(); return NextStmt()
            if v == "drop":      return self.parse_drop()
            if v == "verify":    return self.parse_verify()
            if v == "emit":      return self.parse_emit()
            if v == "expand":    return self.parse_expand()
            if v == "if":        return self.parse_if_main()
            if v == "export":    return self.parse_export()

        # expression statement (assignment, call, etc.)
        return self.parse_expr_stmt()

    def parse_block(self) -> Block:
        """begin ... end"""
        expect_kw = self.expect_kw
        expect_kw("begin")
        self.skip_newlines()
        stmts = []
        while not self.is_kw("end") and not self.check(TT.EOF):
            stmts.append(self.parse_stmt())
            self.skip_newlines()
        expect_kw("end")
        return Block(stmts)

    # ── Variable declaration ──────────────────────────────────────────────────

    def parse_var_decl(self) -> Node:
        """
        let name : Type := expr
        let name :: Type
        let name := expr
        let name op= expr          (augmented assign)
        let cond begin ... end     (if-statement shorthand)
        """
        self.expect_kw("let")
        t = self.current()

        # let cond begin ... end  — shorthand if
        # Detect: next meaningful token is not IDENT followed by := / :: / :
        # We peek ahead: if after the expression we see 'begin', it's an if-stmt
        # Simplest heuristic: if current token is not a plain IDENT, treat as if-cond
        # More robust: parse expression, then check for 'begin'
        expr = self.parse_expr()

        if self.is_kw("begin"):
            # it's   let <cond> begin ... end [given ...] [otherwise ...]
            return self._finish_if_stmt(expr)

        # It's a variable declaration/assignment
        # expr should be an Identifier at this point
        if not isinstance(expr, Identifier):
            raise ParseError("Expected variable name after 'let'", t)
        name = expr.name

        # optional type annotation
        type_hint = None
        domain    = None

        if self.match(TT.DOMAIN):          # ::
            domain = self._read_type()
            # no value follows a domain-only declaration
            if not self.check(TT.ASSIGN):
                return VarDecl(name, type_hint, domain, None)

        elif self.match(TT.COLON):         # :
            type_hint = self._read_type()

        # assignment
        if self.match(TT.ASSIGN):          # :=
            value = self.parse_expr()
            return VarDecl(name, type_hint, domain, value)

        # augmented assignment  +=  -=  *=  /=
        for (tt, op) in [(TT.PLUSEQ,"+="), (TT.MINUSEQ,"-="),
                         (TT.STAREQ,"*="), (TT.SLASHEQ,"/=")]:
            if self.match(tt):
                value = self.parse_expr()
                return Assign(Identifier(name), op, value)

        return VarDecl(name, type_hint, domain, None)

    def _read_type(self) -> str:
        """Read a simple type name (keyword, mathset, or ident)."""
        t = self.current()
        if t.type in (TT.KEYWORD, TT.MATHSET, TT.IDENT):
            self.advance()
            return t.value
        raise ParseError("Expected type name", t)

    # ── If statement ──────────────────────────────────────────────────────────

    def _finish_if_stmt(self, first_cond: Node) -> IfStmt:
        """Called after   let <cond>   has been parsed and 'begin' is next."""
        branches = []
        body = self.parse_block()
        branches.append((first_cond, body))
        self.skip_newlines()

        while self.is_kw("given"):
            self.advance()
            cond = self.parse_expr()
            body = self.parse_block()
            branches.append((cond, body))
            self.skip_newlines()

        otherwise = None
        if self.is_kw("otherwise"):
            self.advance()
            otherwise = self.parse_block()

        return IfStmt(branches, otherwise)

    # ── Function definition ───────────────────────────────────────────────────

    def parse_func_def(self, is_spawn: bool = False) -> FuncDef:
        """where name(params) : ReturnType begin ... end"""
        self.expect_kw("where")
        name = self.expect(TT.IDENT).value
        self.expect(TT.LPAREN)
        params = self._parse_params()
        self.expect(TT.RPAREN)

        return_type = None
        if self.match(TT.COLON):
            return_type = self._read_type()

        body = self.parse_block()
        return FuncDef(name, params, return_type, body, is_spawn)

    def _parse_params(self) -> List[Param]:
        params = []
        while not self.check(TT.RPAREN) and not self.check(TT.EOF):
            variadic = bool(self.match(TT.ELLIPSIS))
            name = self.expect(TT.IDENT).value
            type_hint = None
            if self.match(TT.COLON):
                type_hint = self._read_type()
            params.append(Param(name, type_hint, variadic))
            if not self.match(TT.COMMA):
                break
        return params

    # ── spawn where ... ───────────────────────────────────────────────────────

    def parse_spawn_stmt(self) -> FuncDef:
        self.expect_kw("spawn")
        if self.is_kw("where"):
            return self.parse_func_def(is_spawn=True)
        # spawn expr  (statement form of collect)
        value = self.parse_expr()
        return ExprStmt(SpawnExpr(value))

    # ── report ────────────────────────────────────────────────────────────────

    def parse_return(self) -> ReturnStmt:
        self.expect_kw("report")
        value = self.parse_expr()
        return ReturnStmt(value)

    # ── each ──────────────────────────────────────────────────────────────────

    def parse_each(self) -> EachStmt:
        """each var in expr begin ... end"""
        self.expect_kw("each")
        var = self.expect(TT.IDENT).value
        self.expect_kw("in")
        iter_expr = self.parse_expr()
        body = self.parse_block()
        return EachStmt(var, iter_expr, body)

    # ── repeat-until ──────────────────────────────────────────────────────────

    def parse_repeat(self) -> RepeatStmt:
        """repeat begin ... end until cond"""
        self.expect_kw("repeat")
        body = self.parse_block()
        self.skip_newlines()
        self.expect_kw("until")
        cond = self.parse_expr()
        return RepeatStmt(body, cond)

    # ── given / case  (pattern matching) ─────────────────────────────────────

    def parse_match(self) -> MatchStmt:
        """given expr: | case val -> block | otherwise -> block"""
        self.expect_kw("given")
        subject = self.parse_expr()
        self.expect(TT.COLON)
        self.skip_newlines()

        cases   = []
        default = None

        while self.is_kw("case") or self.is_kw("otherwise"):
            if self.is_kw("otherwise"):
                self.advance()
                self.expect(TT.ARROW)
                default = self._parse_inline_block()
                break
            self.advance()   # case
            val = self.parse_expr()
            self.expect(TT.ARROW)
            blk = self._parse_inline_block()
            cases.append((val, blk))
            self.skip_newlines()

        return MatchStmt(subject, cases, default)

    def _parse_inline_block(self) -> Block:
        """After ->, either a begin...end block or a single expression."""
        self.skip_newlines()
        if self.is_kw("begin"):
            return self.parse_block()
        stmt = self.parse_stmt()
        return Block([stmt])

    # ── check / catch / resolve / always ─────────────────────────────────────

    def parse_check(self) -> CheckStmt:
        self.expect_kw("check")
        body = self.parse_block()
        self.skip_newlines()

        catches = []
        while self.is_kw("catch"):
            self.advance()
            error_type = None
            alias      = None
            t = self.current()
            # A type name may precede `as` (`catch SomeError as e`), but a
            # bare `catch as e` (no type filter) must not have "as" itself
            # mistaken for the type name — that was swallowing the
            # following alias and breaking `catch as e begin ... end`.
            if t.type in (TT.IDENT, TT.KEYWORD) and t.value != "as":
                error_type = self.advance().value
            if self.is_kw("as"):
                self.advance()
                alias = self.expect(TT.IDENT).value
            catch_body = self.parse_block()
            catches.append(CatchClause(error_type, alias, catch_body))
            self.skip_newlines()

        resolve = None
        if self.is_kw("resolve"):
            self.advance()
            resolve = self.parse_block()
            self.skip_newlines()

        always = None
        if self.is_kw("always"):
            self.advance()
            always = self.parse_block()

        return CheckStmt(body, catches, resolve, always)

    # ── abort ─────────────────────────────────────────────────────────────────

    def parse_abort(self) -> AbortStmt:
        self.expect_kw("abort")
        value = self.parse_expr()
        cause = None
        if self.is_kw("cause"):
            self.advance()
            cause = self.parse_expr()
        return AbortStmt(value, cause)

    # ── using / from ─────────────────────────────────────────────────────────

    def parse_using(self) -> Node:
        self.expect_kw("using")

        # using expr as name begin ... end   (context manager)
        # Peek: if after the module name we find 'as' followed by ident then 'begin'
        # we distinguish by checking for begin after the alias
        module_tok = self.current()

        # Could be a context-manager or a module import
        # Try parsing as expression first
        expr = self.parse_expr()

        if self.is_kw("as"):
            self.advance()
            alias = self.expect(TT.IDENT).value
            if self.is_kw("begin"):
                body = self.parse_block()
                return UsingAsStmt(expr, alias, body)
            # regular import with alias
            name = expr.name if isinstance(expr, Identifier) else str(expr)
            return UsingStmt(name, alias)

        name = expr.name if isinstance(expr, Identifier) else str(expr)
        return UsingStmt(name, None)

    def parse_from(self) -> FromStmt:
        """from module provide x, y, z"""
        self.expect_kw("from")
        module = self.expect(TT.IDENT).value
        self.expect_kw("provide")
        names = [self.expect(TT.IDENT).value]
        while self.match(TT.COMMA):
            names.append(self.expect(TT.IDENT).value)
        return FromStmt(module, names)

    # ── structure ─────────────────────────────────────────────────────────────

    def parse_structure(self) -> StructDef:
        """structure Name (immutable)? extends Base? := ... end"""
        self.expect_kw("structure")
        name = self.expect(TT.IDENT).value

        immutable = False
        if self.match(TT.LPAREN):
            if self.is_kw("immutable"):
                self.advance()
                immutable = True
            self.expect(TT.RPAREN)

        base = None
        if self.is_kw("extends"):
            self.advance()
            base = self.expect(TT.IDENT).value

        self.expect(TT.ASSIGN)
        self.skip_newlines()

        members = []
        while not self.is_kw("end") and not self.check(TT.EOF):
            is_static = False
            is_fixed  = False
            # `static` and `fixed`/`immutable` are member modifiers that
            # can prefix either a `property` field or a `where` method.
            while self.is_kw("static") or self.is_kw("fixed") or self.is_kw("immutable"):
                if self.is_kw("static"):
                    is_static = True
                else:
                    is_fixed = True
                self.advance()

            if self.is_kw("where"):
                members.append(self.parse_func_def())
            elif self.is_kw("create"):
                members.append(self._parse_constructor())
            elif self.is_kw("property"):
                self.advance()
                members.append(self._parse_struct_field(is_static, is_fixed))
            elif self.current().type == TT.IDENT:
                # bare field: name [: Type] [:= default]
                members.append(self._parse_struct_field(is_static, is_fixed))
            else:
                break
            self.skip_newlines()

        self.expect_kw("end")
        return StructDef(name, base, immutable, members)

    def expect_field_name(self) -> str:
        """A struct field / property name: IDENT, or a KEYWORD used as a
        field name (e.g. `next`, `prev`, `type`) — common for linked
        structures where the natural name collides with a reserved word."""
        t = self.current()
        if t.type in (TT.IDENT, TT.KEYWORD):
            self.advance()
            return t.value
        raise ParseError("Expected a field name", t)

    def _parse_struct_field(self, is_static: bool, is_fixed: bool) -> StructField:
        """name [: Type] [:= default_expr]  (the 'property'/'static'/'fixed' prefix, if any, is already consumed)"""
        fname = self.expect_field_name()
        ftype = None
        if self.match(TT.COLON):
            ftype = self._read_type()
        default = None
        if self.match(TT.ASSIGN):
            default = self.parse_expr()
        return StructField(fname, ftype, default, is_static, is_fixed)

    def _parse_constructor(self) -> FuncDef:
        """create(params) begin ... end"""
        self.expect_kw("create")
        self.expect(TT.LPAREN)
        params = self._parse_params()
        self.expect(TT.RPAREN)
        body = self.parse_block()
        return FuncDef("create", params, None, body)

    # ── misc statements ───────────────────────────────────────────────────────

    def parse_drop(self) -> DropStmt:
        self.expect_kw("drop")
        name = self.expect(TT.IDENT).value
        return DropStmt(name)

    def parse_verify(self) -> VerifyStmt:
        self.expect_kw("verify")
        return VerifyStmt(self.parse_expr())

    def parse_emit(self) -> EmitStmt:
        self.expect_kw("emit")
        return EmitStmt(self.parse_expr())

    def parse_expand(self) -> ExpandStmt:
        self.expect_kw("expand")
        return ExpandStmt(self.parse_expr())

    def parse_if_main(self) -> IfMain:
        """if main: begin ... end"""
        self.expect_kw("if")
        self.expect_kw("main")
        self.expect(TT.COLON)
        self.skip_newlines()
        body = self.parse_block()
        return IfMain(body)

    def parse_export(self) -> ExprStmt:
        self.expect_kw("export")
        name = self.expect(TT.IDENT).value
        return ExprStmt(Identifier(f"__export_{name}"))

    def parse_expr_stmt(self) -> ExprStmt:
        expr = self.parse_expr()
        # Check for augmented assignment
        for (tt, op) in [(TT.PLUSEQ,"+="), (TT.MINUSEQ,"-="),
                         (TT.STAREQ,"*="), (TT.SLASHEQ,"/=")]:
            if self.match(tt):
                value = self.parse_expr()
                return ExprStmt(Assign(expr, op, value))
        if self.match(TT.ASSIGN):
            value = self.parse_expr()
            return ExprStmt(Assign(expr, ":=", value))
        return ExprStmt(expr)

    # ══════════════════════════════════════════════════════════════════════════
    #  Expression parsing  (operator precedence via recursive descent)
    #
    #  Precedence (lowest → highest):
    #    1. Ternary          cond ? a : b
    #    2. Logical OR       ||
    #    3. Logical AND      &&
    #    4. Logical NOT      !!
    #    5. Comparison       === =!= < > <= >=
    #    6. Additive         + -
    #    7. Multiplicative   * / // %
    #    8. Power            **  (right-associative)
    #    9. Unary            - !!
    #   10. Postfix          call () , subscript [] , projection '
    #   11. Primary          literals, identifiers, grouped exprs
    # ══════════════════════════════════════════════════════════════════════════

    def parse_expr(self) -> Node:
        return self.parse_ternary()

    def parse_ternary(self) -> Node:
        """cond ? then : else"""
        node = self.parse_or()
        if self.match(TT.QUESTION):
            then_expr = self.parse_or()
            self.expect(TT.COLON)
            else_expr = self.parse_ternary()
            return Ternary(node, then_expr, else_expr)
        return node

    def parse_or(self) -> Node:
        node = self.parse_and()
        while self.match(TT.OR):
            node = BinaryOp("||", node, self.parse_and())
        return node

    def parse_and(self) -> Node:
        node = self.parse_not()
        while self.match(TT.AND):
            node = BinaryOp("&&", node, self.parse_not())
        return node

    def parse_not(self) -> Node:
        if self.match(TT.NOT):
            return UnaryOp("!!", self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self) -> Node:
        node = self.parse_set_ops()
        CMP = {TT.EQ: "===", TT.NEQ: "=!=", TT.LT: "<",
               TT.GT: ">",   TT.LTE: "<=",  TT.GTE: ">="}
        while self.current().type in CMP:
            op  = CMP[self.advance().type]
            rhs = self.parse_set_ops()
            node = BinaryOp(op, node, rhs)
        return node

    _SET_OPS = {"union", "intersect", "exclude", "cart"}

    def parse_set_ops(self) -> Node:
        """Left-associative infix set operators: union intersect exclude cart"""
        node = self.parse_additive()
        while self.current().type == TT.KEYWORD and self.current().value in self._SET_OPS:
            op  = self.advance().value        # consume the keyword
            rhs = self.parse_additive()
            node = BinaryOp(op, node, rhs)
        return node

    def parse_additive(self) -> Node:
        node = self.parse_multiplicative()
        while self.current().type in (TT.PLUS, TT.MINUS):
            op  = self.advance().value
            rhs = self.parse_multiplicative()
            node = BinaryOp(op, node, rhs)
        return node

    def parse_multiplicative(self) -> Node:
        node = self.parse_power()
        OPS = {TT.STAR: "*", TT.SLASH: "/",
               TT.DOUBLESLASH: "//", TT.PERCENT: "%"}
        while self.current().type in OPS:
            op  = OPS[self.advance().type]
            rhs = self.parse_power()
            node = BinaryOp(op, node, rhs)
        return node

    def parse_power(self) -> Node:
        """Right-associative: 2 ** 3 ** 2  ==>  2 ** (3 ** 2)"""
        node = self.parse_unary()
        if self.match(TT.STARSTAR):
            return BinaryOp("**", node, self.parse_power())
        return node

    def parse_unary(self) -> Node:
        if self.match(TT.MINUS):
            return UnaryOp("-", self.parse_unary())
        if self.match(TT.NOT):
            return UnaryOp("!!", self.parse_unary())
        if self.match(TT.HASH):
            return LenOp(self.parse_postfix())
        return self.parse_postfix()

    def parse_postfix(self) -> Node:
        """Handles call(), subscript[], and projection'"""
        node = self.parse_primary()
        while True:
            if self.match(TT.LPAREN):
                # function call
                args = []
                while not self.check(TT.RPAREN) and not self.check(TT.EOF):
                    args.append(self.parse_expr())
                    if not self.match(TT.COMMA):
                        break
                self.expect(TT.RPAREN)
                node = Call(node, args)

            elif self.match(TT.PRIME):
                # projection: obj'field or obj'method(...)
                # Field names may legitimately collide with reserved words
                # (e.g. linked-list `next`/`prev` fields), so accept a
                # KEYWORD token here too, not just IDENT.
                field = self.expect_field_name()
                node = Projection(node, field)

            elif self.match(TT.LBRACKET):
                # subscript or slice: S_{i} is lexed as S [ i ]
                # Also handles a[1..3 by 2]
                idx = self.parse_expr()
                if self.match(TT.DOTDOT):
                    stop = self.parse_expr()
                    step = None
                    if self.is_kw("by"):
                        self.advance()
                        step = self.parse_expr()
                    self.expect(TT.RBRACKET)
                    node = Slice(node, idx, stop, step)
                else:
                    self.expect(TT.RBRACKET)
                    node = Subscript(node, idx)

            elif (self.current().type == TT.IDENT and self.current().value == "rt"
                  and self.peek(1).type == TT.LPAREN):
                # {n}rt(x) — nth root notation: degree is the preceding node
                self.advance()  # consume 'rt'
                self.expect(TT.LPAREN)
                arg = self.parse_expr()
                self.expect(TT.RPAREN)
                node = Call(Identifier("nrt"), [node, arg])

            elif self.match(TT.UNDERSCORE):
                # S_{i}  subscript via underscore notation
                self.expect(TT.LBRACE)
                idx = self.parse_expr()
                self.expect(TT.RBRACE)
                node = Subscript(node, idx)

            else:
                break
        return node

    # ── Primary expressions ───────────────────────────────────────────────────

    def parse_primary(self) -> Node:
        t = self.current()

        # Literals
        if t.type == TT.INTEGER:
            self.advance(); return Literal(t.value)
        if t.type == TT.REAL:
            self.advance(); return Literal(t.value)
        if t.type == TT.BOOL:
            self.advance(); return Literal(t.value)
        if t.type == TT.NULL:
            self.advance(); return Literal(None)

        # String
        if t.type == TT.STRING:
            self.advance()
            if isinstance(t.value, tuple) and t.value[0] == "s:":
                return InterpolatedString(t.value[1])
            return Literal(t.value)

        # Math sets: ZZ RR CC ...
        # If followed by '(' treat as a callable identifier (type constructor)
        if t.type == TT.MATHSET:
            self.advance()
            if self.check(TT.LPAREN):
                return Identifier(t.value)
            return MathSet(t.value)

        # Identifiers & keywords used as expressions
        if t.type in (TT.IDENT, TT.KEYWORD):
            v = t.value

            # collect expr
            if v == "collect":
                self.advance()
                return CollectExpr(self.parse_expr())

            # spawn expr
            if v == "spawn":
                self.advance()
                return SpawnExpr(self.parse_expr())

            # fn(params) => expr
            if v == "fn":
                return self.parse_lambda()

            self.advance()
            return Identifier(v)

        # Grouped expression  ( expr )
        if t.type == TT.LPAREN:
            self.advance()
            node = self.parse_expr()
            self.expect(TT.RPAREN)
            return node

        # List literal or list comprehension  [ ... ]
        if t.type == TT.LBRACKET:
            return self.parse_list_or_comp()

        # Set / Range / Mapping literal or comprehension  { ... }
        if t.type == TT.LBRACE:
            return self.parse_brace_expr()

        # Generator comprehension  ⟨ ... ⟩
        if t.type == TT.LANGLE:
            return self.parse_generator_comp()

        # Hash (length)  #expr — already handled in parse_unary, but keep for safety
        if t.type == TT.HASH:
            self.advance()
            return LenOp(self.parse_postfix())

        raise ParseError("Unexpected token in expression", t)

    # ── Lambda ────────────────────────────────────────────────────────────────

    def parse_lambda(self) -> LambdaExpr:
        """fn(params) => expr"""
        self.expect_kw("fn")
        self.expect(TT.LPAREN)
        params = self._parse_params()
        self.expect(TT.RPAREN)
        self.expect(TT.FATARROW)
        body = self.parse_expr()
        return LambdaExpr(params, body)

    # ── List / comprehension ──────────────────────────────────────────────────

    def parse_list_or_comp(self) -> Node:
        """[ expr | var in iter, cond* ]  or  [e1, e2, e3]"""
        self.expect(TT.LBRACKET)
        if self.check(TT.RBRACKET):
            self.advance()
            return ListExpr([])

        first = self.parse_expr()

        # comprehension:  [expr | var in iter]
        if self.match(TT.PIPE):
            var  = self.expect(TT.IDENT).value
            self.expect_kw("in")
            iter_expr  = self.parse_expr()
            conditions = []
            while self.match(TT.COMMA):
                conditions.append(self.parse_expr())
            self.expect(TT.RBRACKET)
            return ListComp(first, var, iter_expr, conditions)

        # regular list
        elements = [first]
        while self.match(TT.COMMA):
            if self.check(TT.RBRACKET): break
            elements.append(self.parse_expr())
        self.expect(TT.RBRACKET)
        return ListExpr(elements)

    # ── Brace expressions: set / mapping / range / comprehension ─────────────

    def parse_brace_expr(self) -> Node:
        self.expect(TT.LBRACE)

        if self.check(TT.RBRACE):
            self.advance()
            return SetExpr([])   # empty set

        first = self.parse_expr()

        # Range:  {1..10}
        if self.match(TT.DOTDOT):
            stop = self.parse_expr()
            self.expect(TT.RBRACE)
            return Range(first, stop)

        # Mapping literal:  {key: val, ...}
        if self.match(TT.COLON):
            val = self.parse_expr()
            pairs = [(first, val)]

            # Mapping comprehension:  {key : val | (k,v) in iter}
            if self.match(TT.PIPE):
                var = self.expect(TT.IDENT).value
                self.expect_kw("in")
                iter_expr = self.parse_expr()
                self.expect(TT.RBRACE)
                return MappingComp(first, val, var, iter_expr)

            while self.match(TT.COMMA):
                if self.check(TT.RBRACE): break
                k = self.parse_expr()
                self.expect(TT.COLON)
                v = self.parse_expr()
                pairs.append((k, v))
            self.expect(TT.RBRACE)
            return MappingExpr(pairs)

        # Set comprehension:  {expr | var in iter}
        if self.match(TT.PIPE):
            var = self.expect(TT.IDENT).value
            self.expect_kw("in")
            iter_expr  = self.parse_expr()
            conditions = []
            while self.match(TT.COMMA):
                conditions.append(self.parse_expr())
            self.expect(TT.RBRACE)
            return SetComp(first, var, iter_expr, conditions)

        # Set literal:  {1, 2, 3}
        elements = [first]
        while self.match(TT.COMMA):
            if self.check(TT.RBRACE): break
            elements.append(self.parse_expr())
        self.expect(TT.RBRACE)
        return SetExpr(elements)

    # ── Generator comprehension  ⟨expr | var in iter⟩ ────────────────────────

    def parse_generator_comp(self) -> GeneratorComp:
        self.expect(TT.LANGLE)
        expr = self.parse_expr()
        self.expect(TT.PIPE)
        var  = self.expect(TT.IDENT).value
        self.expect_kw("in")
        iter_expr = self.parse_expr()
        self.expect(TT.RANGLE)
        return GeneratorComp(expr, var, iter_expr)


# ══════════════════════════════════════════════════════════════════════════════
#  Pretty printer
# ══════════════════════════════════════════════════════════════════════════════

def pretty(node: Node, indent: int = 0) -> str:
    pad  = "  " * indent
    pad2 = "  " * (indent + 1)

    if isinstance(node, Program):
        body = "\n".join(pretty(s, indent) for s in node.body)
        return f"Program:\n{body}"

    if isinstance(node, Block):
        inner = "\n".join(pretty(s, indent + 1) for s in node.stmts)
        return f"{pad}Block:\n{inner}"

    if isinstance(node, VarDecl):
        parts = [f"{pad}VarDecl '{node.name}'"]
        if node.domain:    parts.append(f"{pad2}domain::{node.domain}")
        if node.type_hint: parts.append(f"{pad2}type: {node.type_hint}")
        if node.value:     parts.append(f"{pad2}value:\n{pretty(node.value, indent+2)}")
        return "\n".join(parts)

    if isinstance(node, FuncDef):
        spawn = " [spawn]" if node.is_spawn else ""
        params = ", ".join(
            f"{'...' if p.variadic else ''}{p.name}" +
            (f":{p.type_hint}" if p.type_hint else "")
            for p in node.params
        )
        ret = f" -> {node.return_type}" if node.return_type else ""
        return (f"{pad}FuncDef{spawn} '{node.name}'({params}){ret}:\n"
                f"{pretty(node.body, indent+1)}")

    if isinstance(node, ReturnStmt):
        return f"{pad}Return:\n{pretty(node.value, indent+1)}"

    if isinstance(node, IfStmt):
        lines = [f"{pad}If:"]
        for cond, blk in node.branches:
            lines.append(f"{pad2}cond:\n{pretty(cond, indent+2)}")
            lines.append(pretty(blk, indent+2))
        if node.otherwise:
            lines.append(f"{pad2}otherwise:")
            lines.append(pretty(node.otherwise, indent+2))
        return "\n".join(lines)

    if isinstance(node, EachStmt):
        return (f"{pad}Each '{node.var}' in:\n{pretty(node.iter, indent+1)}\n"
                f"{pretty(node.body, indent+1)}")

    if isinstance(node, RepeatStmt):
        return (f"{pad}Repeat:\n{pretty(node.body, indent+1)}\n"
                f"{pad2}until:\n{pretty(node.condition, indent+2)}")

    if isinstance(node, BinaryOp):
        return (f"{pad}BinaryOp '{node.op}':\n"
                f"{pretty(node.left, indent+1)}\n"
                f"{pretty(node.right, indent+1)}")

    if isinstance(node, UnaryOp):
        return f"{pad}UnaryOp '{node.op}':\n{pretty(node.operand, indent+1)}"

    if isinstance(node, LenOp):
        return f"{pad}Len:\n{pretty(node.operand, indent+1)}"

    if isinstance(node, Call):
        args = "\n".join(pretty(a, indent+1) for a in node.args)
        return f"{pad}Call:\n{pretty(node.callee, indent+1)}\n{pad2}args:\n{args}"

    if isinstance(node, Projection):
        return f"{pad}Projection '{node.field}':\n{pretty(node.obj, indent+1)}"

    if isinstance(node, Subscript):
        return f"{pad}Subscript:\n{pretty(node.obj, indent+1)}\n{pretty(node.index, indent+1)}"

    if isinstance(node, Slice):
        step = f"\n{pretty(node.step, indent+1)}" if node.step else ""
        return (f"{pad}Slice:\n{pretty(node.obj, indent+1)}\n"
                f"{pretty(node.start, indent+1)}\n{pretty(node.stop, indent+1)}{step}")

    if isinstance(node, Literal):
        return f"{pad}Literal {node.value!r}"

    if isinstance(node, InterpolatedString):
        return f"{pad}InterpolatedString {node.raw!r}"

    if isinstance(node, Identifier):
        return f"{pad}Ident '{node.name}'"

    if isinstance(node, MathSet):
        return f"{pad}MathSet '{node.name}'"

    if isinstance(node, LambdaExpr):
        params = ", ".join(p.name for p in node.params)
        return f"{pad}Lambda ({params}):\n{pretty(node.body, indent+1)}"

    if isinstance(node, ListExpr):
        elems = "\n".join(pretty(e, indent+1) for e in node.elements)
        return f"{pad}List:\n{elems}"

    if isinstance(node, SetExpr):
        elems = "\n".join(pretty(e, indent+1) for e in node.elements)
        return f"{pad}Set:\n{elems}"

    if isinstance(node, Range):
        return f"{pad}Range:\n{pretty(node.start, indent+1)}\n{pretty(node.stop, indent+1)}"

    if isinstance(node, ListComp):
        return (f"{pad}ListComp '{node.var}' in:\n{pretty(node.iter, indent+1)}\n"
                f"{pad2}expr:\n{pretty(node.expr, indent+2)}")

    if isinstance(node, SetComp):
        return (f"{pad}SetComp '{node.var}' in:\n{pretty(node.iter, indent+1)}\n"
                f"{pad2}expr:\n{pretty(node.expr, indent+2)}")

    if isinstance(node, Ternary):
        return (f"{pad}Ternary:\n{pad2}cond:\n{pretty(node.condition, indent+2)}\n"
                f"{pad2}then:\n{pretty(node.then_expr, indent+2)}\n"
                f"{pad2}else:\n{pretty(node.else_expr, indent+2)}")

    if isinstance(node, Assign):
        return (f"{pad}Assign '{node.op}':\n{pretty(node.target, indent+1)}\n"
                f"{pretty(node.value, indent+1)}")

    if isinstance(node, ExprStmt):
        return pretty(node.expr, indent)

    if isinstance(node, (SkipStmt, StopStmt, NextStmt)):
        return f"{pad}{type(node).__name__}"

    if isinstance(node, DropStmt):
        return f"{pad}Drop '{node.name}'"

    if isinstance(node, VerifyStmt):
        return f"{pad}Verify:\n{pretty(node.expr, indent+1)}"

    if isinstance(node, EmitStmt):
        return f"{pad}Emit:\n{pretty(node.value, indent+1)}"

    if isinstance(node, ReturnStmt):
        return f"{pad}Return:\n{pretty(node.value, indent+1)}"

    if isinstance(node, CheckStmt):
        lines = [f"{pad}Check:", pretty(node.body, indent+1)]
        for c in node.catches:
            lines.append(f"{pad2}Catch {c.error_type or '*'}" +
                         (f" as {c.alias}" if c.alias else "") + ":")
            lines.append(pretty(c.body, indent+2))
        if node.resolve: lines += [f"{pad2}Resolve:", pretty(node.resolve, indent+2)]
        if node.always:  lines += [f"{pad2}Always:",  pretty(node.always,  indent+2)]
        return "\n".join(lines)

    if isinstance(node, AbortStmt):
        cause = f"\n{pad2}cause:\n{pretty(node.cause, indent+2)}" if node.cause else ""
        return f"{pad}Abort:\n{pretty(node.value, indent+1)}{cause}"

    if isinstance(node, UsingStmt):
        alias = f" as '{node.alias}'" if node.alias else ""
        return f"{pad}Using '{node.module}'{alias}"

    if isinstance(node, FromStmt):
        return f"{pad}From '{node.module}' provide {node.names}"

    if isinstance(node, StructDef):
        lines = [f"{pad}Structure '{node.name}'" +
                 (f" extends '{node.base}'" if node.base else "") +
                 (" (immutable)" if node.immutable else "") + ":"]
        for m in node.members:
            lines.append(pretty(m, indent+1))
        return "\n".join(lines)

    if isinstance(node, StructField):
        return f"{pad}Field '{node.name}'" + (f" : {node.type_hint}" if node.type_hint else "")

    if isinstance(node, MatchStmt):
        lines = [f"{pad}Match:\n{pretty(node.subject, indent+1)}"]
        for val, blk in node.cases:
            lines.append(f"{pad2}Case:\n{pretty(val, indent+2)}")
            lines.append(pretty(blk, indent+2))
        if node.default:
            lines.append(f"{pad2}Otherwise:")
            lines.append(pretty(node.default, indent+2))
        return "\n".join(lines)

    if isinstance(node, CollectExpr):
        return f"{pad}Collect:\n{pretty(node.value, indent+1)}"

    if isinstance(node, SpawnExpr):
        return f"{pad}Spawn:\n{pretty(node.value, indent+1)}"

    if isinstance(node, IfMain):
        return f"{pad}IfMain:\n{pretty(node.body, indent+1)}"

    return f"{pad}{type(node).__name__}(...)"


# ══════════════════════════════════════════════════════════════════════════════
#  Test driver
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    sample = """
-- Axioma parser test

using math
from geometry provide Circle

where greet(name : CharSequence) : CharSequence begin
  report s"Hello, {name}!"
end

let nums := [1, 2, 3, 4, 5]
let squares := [x ** 2 | x in {1..10}]
let evens := {n | n in nums, n % 2 === 0}

let active : Bool := T
let integers :: ZZ

each n in nums begin
  let n % 2 === 0 begin
    out(n)
  end given n > 3 begin
    out(s"big odd: {n}")
  end otherwise begin
    skip
  end
end

let count := 0
repeat begin
  count += 1
end until count === 5

let label := count > 3 ? "big" : "small"

where fib(n : ZZ) : ZZ begin
  let n <= 1 begin
    report n
  end
  report fib(n - 1) + fib(n - 2)
end

structure Point :=
  x : RR
  y : RR
  create(px : RR, py : RR) begin
    this'x := px
    this'y := py
  end
  where distance() : RR begin
    report (this'x ** 2 + this'y ** 2) ** 0.5
  end
end

check begin
  let result := 10
end catch Error as e begin
  abort s"Failed: {e}" cause e
end always begin
  out("done")
end

verify #nums === 5

if main:
begin
  out(greet("World"))
end
"""

    print("═" * 56)
    print("  AXIOMA PARSER — Abstract Syntax Tree")
    print("═" * 56)
    tokens = Lexer(sample).tokenize()
    ast    = Parser(tokens).parse()
    print(pretty(ast))
    print("═" * 56)
