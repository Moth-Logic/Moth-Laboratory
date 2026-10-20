<p align="center">
  <img src="images/Moth%20Laboratory.png" alt="Moth Laboratory logo" width="650">
</p>

<h1 align="center">Moth Laboratory</h1>

<p align="center">
  <em>Colección de proyectos, scripts, experimentos y varas varias.</em><br>
  Some of it solves a real problem. Some of it exists because I wanted to know if I could. Both count.
</p>

<p align="center">
  <img alt="C++" src="https://img.shields.io/badge/C%2B%2B-20-00599C?style=for-the-badge&logo=cplusplus&logoColor=white">
  <img alt="Java" src="https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Lua" src="https://img.shields.io/badge/Lua-2C2D72?style=for-the-badge&logo=lua&logoColor=white">
  <img alt="Assembly" src="https://img.shields.io/badge/Assembly-NASM%20x86--64-6E4C13?style=for-the-badge">
</p>

<p align="center">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Windows%20%7C%20Debian-0078D6?style=for-the-badge&logo=linux&logoColor=white">
  <img alt="Status" src="https://img.shields.io/badge/Status-En%20desarrollo-yellow?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/License-Unlicense-blue?style=for-the-badge">
</p>

---

## So, what is this?

This is my personal lab. It is a pile of things I built to learn a language, to make a boring task less boring, or simply because an idea would not leave me alone until I typed it out.

There is no grand architecture here. Each language gets its own folder, each folder has its own thing going on, and everything is small enough to read in an afternoon. That is on purpose.

## The spaces

| Folder | Language | What lives there |
| --- | --- | --- |
| [Python Workshop](Python%20Workshop) | Python | One-file exercises, plus two very different versions of Snake. |
| [Lua Sandbox](Lua%20Sandbox) | Lua | **Byte Cat**, a terminal virtual pet. Also a practice file. |
| [C++ Forge](C%2B%2B%20Forge) | C++20 | Workshop space for C++ projects. Currently starts with Hello World. |
| [Java Playground](Java%20Playground) | Java | Java programs and experiments. Currently starts with Hello World. |
| [Assembly Studio](Assembly%20Studio) | x86-64 NASM | Low-level experiments that talk to the Linux kernel directly. |
| [Axioma](Axioma) | Python, C++, JavaScript | A programming language of my own, its IDE, and a calculator built alongside it. |

---

## Python Workshop

The exercises are in `Python Workshop/Python Excercises`. Yes, that is how the folder is spelled, and at this point it has become part of the furniture. Most files are self-contained answers to a specific problem: primes, the Collatz conjecture, Euclid's GCD, an efficient LCM, factorials, perfect squares, digit histograms, unit and imperial-to-metric conversions, electronic invoices, progressive taxes, file handling, dictionary methods, and a few small puzzles in between. They are mostly written in Spanish because that is how they were assigned. Run any of them with:

```bash
python "Python Workshop/Python Excercises/Es_Primo.py"
```

Then there is Snake, twice. Both versions use a 50×50 matrix and the same basic idea — eat, grow, do not crash — but they grew in different directions:

- **`snake ver.mothie`** adds golden apples and poison cells, and the speed climbs as you eat.
- **`Snake ver.naomi`** is the cleaner, classic version.

Both have their own matrix logic and a pygame window, so install pygame first:

```bash
pip install pygame
```

Then pick a version and run its GUI:

```bash
cd "Python Workshop/snake ver.mothie"
python gui.py
```

Change the folder to `Snake ver.naomi` for the other one. The `snake.py` files hold the game state and rules; `gui.py` is what you actually launch.

---

## Lua Sandbox

### Byte Cat

This is the main event in this folder. Byte is a small cat who lives in your terminal. He has five needs — belly, energy, cleanliness, happiness, and health — and a limited amount of patience for your scheduling.

The good news is that he is not complicated. Feed him, play with him, brush him, and let him sleep. The less good news is that time moves every time you do something, and ignoring a need for long enough will make him sick. If his health reaches zero, that is the end of that life.

To start:

```bash
cd "Lua Sandbox"
lua byte_cat.lua
```

That is it. No dependencies beyond Lua itself (5.1 or newer). On the first run you get to name him. After that, the game picks up from `bytecat_save.txt`, which lives next to the script and is written after every turn. Delete that file if you want a fresh cat.

The menu is short:

- **Feed** opens a small food menu. Kibble is reliable, tuna is the favourite, milk is a treat, and the cookie is a terrible idea that Byte fully supports.
- **Play** burns energy and fixes a bad mood. Too tired to play? He will flop over to make sure you know.
- **Pet** is the low-effort option. He leans in, then pretends he did not.
- **Clean** gets rid of the dust. He tolerates the brush for your sake.
- **Sleep** passes eight hours and refills his energy. Do not put him to bed hungry.
- **Check** shows exact numbers and, frankly, a blunt assessment.
- **Quit** saves and lets him nap.

Little things happen on their own too — sunbeams, hairballs, moths at the window, the occasional zoomie. Sleep comes with dreams. Byte is not hard to keep alive, but he is absolutely judging you.

### The other file

`Hello World.lua` is a practice skeleton: variables, functions, a loop, an `if`, and a small table. It is there for the days when I want to poke at Lua syntax without starting a whole project.

---

## C++ Forge

A workshop for C++20 projects, built mostly with Visual Studio on Windows and g++ on Debian. It currently contains `hello_world.cpp`, which does exactly what it says.

With g++:

```bash
cd "C++ Forge"
g++ -std=c++20 -Wall -Wextra hello_world.cpp -o hello_world
./hello_world
```

From a Visual Studio developer prompt on Windows:

```bat
cl /EHsc /std:c++20 hello_world.cpp
hello_world.exe
```

---

## Java Playground

Programs, small tools and experiments in Java, targeting JDK 17 or newer. Eclipse or VS Code handle the editing. Right now it starts with the traditional greeting:

```bash
cd "Java Playground"
javac HelloWorld.java
java HelloWorld
```

---

## Assembly Studio

Personal x86-64 assembly projects written in NASM syntax for Linux (Debian). The folder is called Assembly Studio, but the code inside is very much a vault of small experiments. The school course uses GAS, so this space is for everything outside of class.

```bash
cd "Assembly Studio"
nasm -f elf64 hello_world.asm -o hello_world.o
ld hello_world.o -o hello_world
./hello_world
```

`hello_world.asm` prints its greeting with two raw Linux system calls and no C library in sight. If you are on Windows, run the same commands inside WSL.

---

## Axioma

Axioma is a programming language I built from scratch. It has a lexer, a parser, an interpreter, structures (linked lists, trees and graphs), its own browser IDE, and a desktop calculator that grew out of the same curiosity.

### The language engine

Everything lives in `Axioma/Axioma Code`:

| File | What it does |
| --- | --- |
| `axioma_lexer.py` | Turns source text into tokens. Also owns the canonical `.axm` extension. |
| `axioma_parser.py` | Turns tokens into an AST and enforces the grammar. |
| `interpreter.py` | Runs the AST and provides the built-in functions. |
| `run_axioma.py` | CLI runner: a file argument or source on stdin. |
| `__init__.py` | Package initializer. |
| `pyrightconfig.json` | Type-checking configuration (Python 3.11). |

Run a program from that folder:

```bash
cd "Axioma/Axioma Code"
python3 run_axioma.py program.axm
python3 run_axioma.py < program.axm
```

Axioma source files use **`.axm`**. The old `.ax` extension is rejected with a message telling you to rename the file, which is a much nicer experience than a confusing parser error.

### What the language can do

Structures are reference types, so linked structures work the way you would hope: `node'next := other_node` aliases instead of copying. On top of that:

- `property name [: Type] [:= default]` declares instance fields, initialized before `create()` runs.
- `static property name [:= default]` shares a field across every instance.
- `fixed` / `immutable` makes a property write-once: settable during construction, locked afterwards. Reassigning it raises a catchable error.
- `is_null(x)` gives you a safe way to check before projecting a field.
- `contains(collection, item)` tests membership in a `Sequence`, `Set`, `Mapping` (keys) or `CharSequence`.
- Typed errors are real: `abort MyErrorStruct(...)` and `catch MyErrorStruct as e` let you build custom exceptions.
- `given` / `case` pattern matching uses the `->` arrow, and interpolated strings (`s"..."`) propagate runtime errors properly.
- Field names can collide with reserved keywords — `next`, `prev`, `type` — which makes natural node fields like `node'next` possible.

Runtime errors carry a line and column, so the message tells you where it happened rather than just what happened.

The engine has had a few cleanup passes worth mentioning. The arrow token used to be unreachable dead code, which silently broke `case value -> block`; struct member parsing and field initialization were rebuilt; typed catches actually filter by type now, including the bare `catch as e` form. On the speed side, builtins no longer construct a fresh interpreter on every call; statement and expression dispatch now use O(1) table lookups; scope lookups are iterative instead of recursive; and the lexer's character table is built once per program.

### The Axioma IDE

Open `Axioma/Axioma IDE.html` in a browser. No Python, no Node, no server. The whole lexer, parser and interpreter are implemented in JavaScript inside the page.

You get two columns: the **editor** on the left and the **console** on the right. Write code, then click **▶ Ejecutar** or press **Ctrl+Enter** (**⌘+Enter** on Mac). Output appears on the right; errors appear in red with the line number.

The **Ejemplos…** menu in the top left has two groups:

- **Básicos** — Hello World, variables, conditionals, loops, functions, lists.
- **Avanzados (TDA, nodos, errores)** — structures, linked lists, trees, graphs and error handling.

Pick one, edit it, run it. **Guardar .axm** downloads the current editor contents, **Abrir .axm** loads a file you already have, and the moon button switches between light and dark themes. If a parser error shows up, the usual suspects are a missing `end`, a missing `begin`, or an unclosed parenthesis.

There is also a full language guide in `Axioma/C#U00f3mo Programar en Axioma.html`, including worked examples for the data structures.

### My First Calculator

The calculator started as a simple `+ - * /` window and kept growing. It is a desktop app in Python, with a modern interface, scientific functions, persistent history, angle modes, a base converter, an ASCII table and a notepad. The evaluator also has a C++ implementation through pybind11, with a pure-Python fallback if you do not compile it.

What it can do:

- Arithmetic with parentheses, `^` powers (right-associative), `%` modulo, and scientific notation like `1e6` and `2.5E-3`.
- Trigonometry (`sin`, `cos`, `tan`, `asin`, `acos`, `atan`) in degrees or radians, plus `sinh`, `cosh`, `tanh`, `sqrt`, `cbrt`, `log`, `ln`, `abs`, `exp`, `ceil`, `floor` and `round`.
- Constants `pi` and `e`.
- A history panel with the last 100 operations. Click an entry to reuse it. It survives restarts in `~/.everything_app/history.json`.
- A DEC/BIN/OCT/HEX converter, an ASCII table for 0–127, and a small notepad.
- Full keyboard input, not just buttons: numbers, function names, operators, `Enter` to evaluate, `Backspace` to delete and `Esc` to clear. `C` clears the whole display, and the `Angle: DEG / RAD` button flips the trig mode.

A few expressions worth trying: `2 + 3 * 4` is `14`, `(2 + 3) * 4` is `20`, `2^3^2` is `512`, `sin(30)` in DEG mode is `0.5`, and `sqrt(16) + log(100)` is `6`. Type something impossible like `5 / 0` and the display tells you why in red instead of throwing a traceback at you.

It needs **Python 3.10 or newer**. On Windows:

```powershell
cd "Axioma/My-First-Calculator"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

On Debian, activate with `source venv/bin/activate` instead. You have to run the activation step again in every new terminal. The requirements pull in `customtkinter` for the interface, `pyinstaller` for the standalone build, and `pybind11` plus `setuptools` for the optional C++ evaluator.

To compile the C++ backend:

```bash
python setup.py build_ext --inplace
```

If you skip that step, the app still runs and quietly uses the Python evaluator. The same is true for the angle mode: the C++ path does not know about DEG/RAD, so that logic lives in the Python fallback.

Tests use only `unittest`:

```bash
python -m unittest        # summary
python -m unittest -v     # one test at a time
```

They cover the lexer, parser, evaluator (including angle mode), base converter, history and ASCII table, with regressions for malformed numbers, overflow cases like `exp(1000)`, and negative-number round trips.

To build a single-file Windows executable:

```powershell
pyinstaller build.spec
```

The result is `dist\MyFirstCalculator.exe`. It runs without Python installed, which makes it easy to hand to someone else. If Windows Defender complains, that is the usual PyInstaller false positive; add an exception for that file.

A few practical notes, because every project eventually needs them: if `python` is not recognized, reinstall Python with "Add Python to PATH" checked. If `pip install` hits permission errors, the virtual environment is probably not active. If the `.exe` opens and immediately closes, run it from a terminal to see the traceback, or temporarily set `console=True` in `build.spec` and rebuild.

The core is deliberately separated from the GUI: `core/` has the lexer, parser, evaluator, history, base converter and ASCII logic, while `gui/app.py` only draws things and delegates. That is why the tests can run without opening a window, and why swapping the evaluator for C++ did not disturb the rest of the app. Still on the list: memory keys (`M+`, `M-`, `MR`) and exact fractions or complex numbers instead of plain floats.

---

## Repository structure

```text
Moth-Laboratory/
├── Assembly Studio/          x86-64 NASM experiments
├── Axioma/
│   ├── Axioma Code/          Language engine and CLI
│   ├── Axioma IDE.html       Browser IDE
│   ├── C#U00f3mo Programar en Axioma.html   Language guide
│   └── My-First-Calculator/  Desktop calculator
├── C++ Forge/                C++20 workshop
├── images/                   README artwork
├── Java Playground/          Java programs
├── Lua Sandbox/              Byte Cat and Lua practice
├── Python Workshop/          Exercises and two Snake games
├── LICENSE
└── README.md
```

## Getting started

Clone the repo, `cd` into whichever folder sounds interesting, and follow that section. There is no monorepo tooling, no root build script, and no hidden setup step. The only prerequisites are the obvious ones: Python 3.10+ for the Python work, Lua 5.1+ for Byte Cat, JDK 17+ for Java, a C++20 compiler for C++ Forge, and NASM on Linux (or WSL) for Assembly Studio.

## License

This project is released into the public domain under the [Unlicense](LICENSE). Copy it, change it, sell it, or do whatever you want with it. Byte Cat would like to be fed either way.
