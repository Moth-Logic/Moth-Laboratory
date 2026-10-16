"""
Axioma Runner
=============
Executes an Axioma (.axm) source file, or reads a program from stdin.

Usage:
    python3 run_axioma.py program.axm      # run a file
    python3 run_axioma.py < program.axm    # pipe source in on stdin
Any error is printed to stderr with a non-zero exit code.
"""
import sys
import io
import os

sys.path.insert(0, os.path.dirname(__file__))

from axioma_lexer import LexerError, SOURCE_EXTENSION
from axioma_parser import ParseError
from interpreter import Interpreter, AxiomaError


def _validate_extension(path: str):
    """Reject anything that isn't a .axm source file with a clear message.

    (Historically Axioma source used the .ax extension; the canonical
    extension is now .axm — see SOURCE_EXTENSION in axioma_lexer.py.)
    """
    if not path.endswith(SOURCE_EXTENSION):
        _, ext = os.path.splitext(path)
        hint = ""
        if ext == ".ax":
            hint = f" (note: Axioma source files now use '{SOURCE_EXTENSION}', not '.ax' — rename the file)"
        print(
            f"error: expected an Axioma source file ending in '{SOURCE_EXTENSION}', "
            f"got '{path}'{hint}",
            file=sys.stderr,
        )
        sys.exit(64)  # EX_USAGE


def main():
    file_arg = None
    for arg in sys.argv[1:]:
        if arg.startswith("-"):
            continue
        file_arg = arg
        break

    if file_arg is not None:
        _validate_extension(file_arg)
        if not os.path.isfile(file_arg):
            print(f"error: no such file: '{file_arg}'", file=sys.stderr)
            sys.exit(66)  # EX_NOINPUT
        with open(file_arg, "r", encoding="utf-8") as f:
            source = f.read()
    else:
        source = sys.stdin.read()

    captured_out = io.StringIO()
    captured_err = io.StringIO()
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = captured_out
    sys.stderr = captured_err
    try:
        interp = Interpreter()
        interp.run(source)
    except (LexerError, ParseError, AxiomaError) as e:
        sys.stderr = old_stderr
        sys.stdout = old_stdout
        output = captured_out.getvalue()
        if output:
            print(output, end="")
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except SystemExit as e:
        exit_code = e.code if e.code is not None else 0
        sys.stderr = old_stderr
        sys.stdout = old_stdout
        output = captured_out.getvalue()
        if output:
            print(output, end="")
        sys.exit(exit_code)
    except Exception as e:
        sys.stderr = old_stderr
        sys.stdout = old_stdout
        output = captured_out.getvalue()
        if output:
            print(output, end="")
        print(f"Internal error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
    finally:
        if sys.stdout is not old_stdout:
            sys.stdout = old_stdout
        if sys.stderr is not old_stderr:
            sys.stderr = old_stderr

    output = captured_out.getvalue()
    if output:
        print(output, end="")


if __name__ == "__main__":
    main()
