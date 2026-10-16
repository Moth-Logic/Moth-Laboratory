# Axioma language files

This bundle contains the Axioma language engine — refactored, bug-fixed, and
extended with abstract-data-type (structure) support for building linked
lists, trees, and graphs directly in Axioma.

## Included files

- `axioma_lexer.py` — lexer and token definitions
- `axioma_parser.py` — parser and syntax rules
- `interpreter.py` — runtime and built-in functions
- `run_axioma.py` — CLI runner (file argument or stdin)
- `__init__.py` — package initializer
- `pyrightconfig.json` — Python 3.11 type-checking configuration

## ⚠️ File extension change: `.ax` → `.axm`

Axioma source files now use the **`.axm`** extension. `run_axioma.py`
validates this and will refuse to run a `.ax` file with a clear message
telling you to rename it. The canonical extension lives in one place:
`axioma_lexer.SOURCE_EXTENSION`.

## Run locally

```bash
python3 run_axioma.py program.axm     # run a file
python3 run_axioma.py < program.axm   # or pipe source on stdin
```

## Bug fixes in this pass

- **`->` (ARROW) was dead code** — a duplicate `-` handler further down
  `_scan_token` could never execute, so `->` always lexed as `MINUS` then
  `GT`. This silently broke `given/case` pattern matching's
  `case value -> block` syntax. Fixed.
- **`property`/`static` struct members crashed the parser** — they were
  routed into method parsing (expecting `where`) instead of being parsed
  as field declarations. Rebuilt struct-member parsing from scratch.
- **Declared struct fields (`property x`, bare `x : Type`) did nothing** —
  parsed into the AST but never read by the interpreter. They're now
  properly initialized (with defaults) before `create()` runs.
- **`s"..."` interpolated strings silently swallowed runtime errors**
  inside `{...}` expressions (`except: return original text`). Removed —
  errors now propagate like any other expression.
- **`catch <Type> as e` never actually filtered by type** (`... or True`
  bug made every catch clause catch everything). Fixed, with backward
  compatible semantics: `abort "message"` is type `Error` (matching the
  manual's `catch Error as e` idiom); `abort SomeStruct(...)` is typed by
  structure name for real custom exception types.
- **`catch as e` (no type filter) mis-parsed** — `as` itself was
  consumed as if it were a type name. Fixed.
- Field names may now collide with reserved keywords (`next`, `prev`,
  `type`, …) — required for natural linked-list/tree/graph field names
  like `node'next`.

## Performance

- `apply`, `select`, `fold`, `sum`, `prod`, `deriv`, `integ` previously
  constructed a **brand-new `Interpreter()`** (rebuilding the entire
  builtins table) on every single function-call — i.e. every loop
  iteration. They now reuse the live interpreter instance.
- `s"..."` interpolation reused this same fix (was also building a fresh
  `Interpreter()` per string).
- Statement/expression dispatch (`exec_stmt` / `eval_expr`) switched from
  an `if/elif` chain to a dict lookup built once per interpreter instance
  — O(1) instead of O(n) per node.
- `Environment.get` / `.assign` / `.drop` switched from recursive scope
  walks to iterative loops (one fewer Python stack frame per enclosing
  scope, on every variable read).
- The lexer's single-character token table is now a module-level
  constant instead of being rebuilt on every character scanned.

## Error messages

Runtime errors (`AxiomaError`) now carry `line`/`col`, populated from the
statement currently executing, e.g.:

```
Cannot reassign 'x' — declared 'fixed' on structure 'Point' (at line 48, col 3)
```

## New language features (Abstract Data Types & references)

Structures were already reference types (Python object semantics), so
linked structures (`node'next := other_node`) already aliased correctly —
no new syntax was needed for that part. What's new:

- **`property name [: Type] [:= default]`** — declared instance fields,
  initialized before `create()` runs.
- **`static property name [:= default]`** — class-level fields shared by
  every instance; read/write via either `Instance'name` or
  `StructName'name`.
- **`fixed` / `immutable` property** — write-once fields: settable during
  construction (inside `create()`), then locked. Reassigning raises a
  catchable error.
- **`is_null(x)`** — safe-dereference check (`Null` fields already fail
  with a clean `AxiomaError` rather than a Python crash when projected).
- **`contains(collection, item)`** — membership test for `Sequence` /
  `Set` / `Mapping` (keys) / `CharSequence`, since there's no infix `in`
  operator outside `each`/comprehensions.
- Typed, catchable custom exceptions: `abort MyErrorStruct(...)` +
  `catch MyErrorStruct as e` — see `_error_type_name` in `interpreter.py`.

See the full guide (`axioma_guide.html` / the published IDE) for worked
linked-list, binary-tree, and graph examples.

# Axioma IDE — How to Use It

The Axioma IDE is a web page where you can write and run programs in the
Axioma language straight from your browser. You don't need to install
anything: no Python, no Node, no extra program. Everything runs on the page.

## 1. Open the IDE

Open the `axioma_ide.html` file (or the link you were given) in your
browser. You'll see two columns:

- **Left (EDITOR):** this is where you write your Axioma code.
- **Right (CONSOLE):** this is where your program's output shows up, or
  the error message if something went wrong.

## 2. Run a program

There are two ways to run the code in the editor:

1. Click the **▶ Ejecutar** button (top center — "Ejecutar" is Spanish
   for "Run").
2. Or use the keyboard shortcut **Ctrl+Enter** (on Mac: **⌘+Enter**).

The result shows up in the console, on the right. If the program has an
error, it appears in red with the line number where it happened.

## 3. Try the examples

In the top left there's a dropdown menu labeled **"Ejemplos…"** ("Examples…").
In there you'll find ready-made programs, organized into two groups:

- **Básicos** ("Basics") — the first thing you should try: Hello World,
  variables, conditionals, loops, functions, lists, etc.
- **Avanzados (TDA, nodos, errores)** ("Advanced: ADTs, nodes, errors") —
  structures (abstract data types), linked lists, trees, graphs, and
  error handling.

Pick one and the code automatically appears in the editor. Then press
**Ejecutar** to see it run. You can freely edit an example's code to
experiment with it.

## 4. Save and open your own files

- **Guardar .axm** ("Save") downloads the code currently in the editor
  as an `.axm` file to your computer.
- **Abrir .axm** ("Open") loads an `.axm` file you already have saved,
  so you can keep editing it.

`.axm` is the official file extension for Axioma source code (the same
way `.py` is for Python or `.java` is for Java).

## 5. Switch theme (light/dark)

The little moon button (☾) in the top right corner switches between
dark and light theme.

## Something's not working — what do I do?

- If you see a red error in the console, read it: it usually tells you
  what went wrong and on which line of your code.
- If the error is a "Parser" error (syntax error), check that you
  haven't forgotten an `end`, a `begin`, or that your parentheses `()`
  are properly closed.
- If you want to start fresh, just clear all the code in the editor and
  write your own, or pick an example from the menu as a starting point.

## What's running under the hood?

The IDE includes a complete implementation of the Axioma language written
in JavaScript (the lexer, the parser, and the interpreter), so everything
runs inside the page itself — it doesn't depend on any external server.
It's the same language as the Python engine (`axioma_lexer.py`,
`axioma_parser.py`, `interpreter.py`), just rewritten for the browser.