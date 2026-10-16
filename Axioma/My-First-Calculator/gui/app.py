"""
gui/app.py
----------
Single-window "everything app" with four tabs:
  1. Calculator     — scientific calculator (delegates to core.Calculator)
                      with DEG/RAD toggle, detailed errors and a
                      persistent click-to-reuse history sidebar
  2. Base Converter — bin / oct / dec / hex conversion with copy buttons
  3. ASCII Table    — interactive, searchable ASCII reference
  4. Notepad        — plain-text scratch pad

Each tab builds its own widgets inside the CTkTabview page.
The GUI only draws and delegates: all logic lives in core/.
"""

from __future__ import annotations
import math
import tkinter as tk
import customtkinter as ctk

from core import (
    ANGLE_DEG,
    ANGLE_RAD,
    Calculator,
    CalculatorError,
    History,
    HistoryEntry,
    convert,
    BaseConverterError,
    generate_table,
    search_table,
)

# Tab names — CTkTabview identifies tabs by label, and the global keyboard
# bindings are guarded with these so keys only affect the visible tab.
_TAB_CALC = "🧮 Calculator"
_TAB_BASE = "🔄 Base Converter"
_TAB_ASCII = "📋 ASCII Table"
_TAB_NOTEPAD = "📝 Notepad"

# --- Visual config -------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_DARK_BG = "#1e1e1e"

# ========================================================================
#  CALCULATOR TAB
# ========================================================================

_BUTTON_LAYOUT = [
    ["sin", "cos", "tan", "asin", "acos"],
    ["√", "log", "ln", "atan", "π"],
    ["e", "(", ")", "%", "^"],
    ["C", "←", "/", "*", ""],
    ["7", "8", "9", "-", ""],
    ["4", "5", "6", "+", ""],
    ["1", "2", "3", "=", ""],
    ["0", ".", "", "", ""],
]

_OPERATORS = {"/", "*", "-", "+", "^", "%"}

_BTN_TEXT = {
    "sin": "sin(", "cos": "cos(", "tan": "tan(",
    "asin": "asin(", "acos": "acos(", "atan": "atan(",
    "√": "sqrt(", "log": "log(", "ln": "ln(",
    "π": "pi", "e": "e",
}


def _btn_color(label: str) -> str:
    if label == "=":
        return "#2fa572"
    if label in ("C", "←"):
        return "#b3413a"
    if label in _BTN_TEXT:
        return "#5a3a8a"
    if label in _OPERATORS or label in ("(", ")"):
        return "#3a3a3a"
    return "#4a4a4a"


# ========================================================================
#  BASE CONVERTER TAB
# ========================================================================

_BASE_KEYS = ["DEC", "BIN", "OCT", "HEX"]
_BASE_LABELS = {"DEC": "Decimal", "BIN": "Binary", "OCT": "Octal", "HEX": "Hexadecimal"}
_BASE_RADIX = {"DEC": 10, "BIN": 2, "OCT": 8, "HEX": 16}


# ========================================================================
#  ASCII TABLE TAB
# ========================================================================

_TABLE_COLUMNS = ("DEC", "HEX", "OCT", "BIN", "CHAR")
_COL_WIDTHS = {"DEC": 60, "HEX": 60, "OCT": 60, "BIN": 100, "CHAR": 60}


# ========================================================================
#  MAIN APP
# ========================================================================

class EverythingApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self._is_dark = True  # track current theme

        self.title("Everything App")
        self.geometry("780x740")
        self.minsize(700, 640)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # -- Header -------------------------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, pady=(10, 4), sticky="ew", padx=16)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="⚡ Everything App",
            font=ctk.CTkFont(size=22, weight="bold"),
            height=40,
        ).grid(row=0, column=0, sticky="w")

        self._theme_btn = ctk.CTkButton(
            header,
            text="🌙 Dark",
            font=ctk.CTkFont(size=13),
            width=90,
            height=32,
            fg_color="#3a3a3a",
            command=self._toggle_theme,
        )
        self._theme_btn.grid(row=0, column=1, sticky="e", padx=(8, 0))

        # -- Tabview ------------------------------------------------------
        self._tabs = ctk.CTkTabview(self, anchor="nw")
        self._tabs.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self._tab_calc = self._tabs.add(_TAB_CALC)
        self._tab_base = self._tabs.add(_TAB_BASE)
        self._tab_ascii = self._tabs.add(_TAB_ASCII)
        self._tab_notepad = self._tabs.add(_TAB_NOTEPAD)

        self._build_calculator_tab()
        self._build_base_converter_tab()
        self._build_ascii_table_tab()
        self._build_notepad_tab()

    # ------------------------------------------------------------------ #
    #  1. CALCULATOR                                                      #
    # ------------------------------------------------------------------ #

    def _build_calculator_tab(self) -> None:
        tab = self._tab_calc
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=0)
        tab.grid_rowconfigure(2, weight=1)

        self._calc = Calculator()
        self._expression = ""
        self._history = History()

        # -- Top bar: DEG/RAD angle-mode toggle ---------------------------
        topbar = ctk.CTkFrame(tab, fg_color="transparent")
        topbar.grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 4), sticky="ew")
        topbar.grid_columnconfigure(1, weight=1)

        self._angle_btn = ctk.CTkButton(
            topbar,
            text="Angle: DEG",
            font=ctk.CTkFont(size=13),
            width=110,
            height=30,
            fg_color="#3a3a3a",
            command=self._toggle_angle_mode,
        )
        self._angle_btn.grid(row=0, column=0, sticky="w")

        self._angle_hint = ctk.CTkLabel(
            topbar,
            text="trig in degrees",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        )
        self._angle_hint.grid(row=0, column=1, sticky="w", padx=10)

        # -- Display (spans buttons + history) -----------------------------
        self._display = ctk.CTkLabel(
            tab,
            text="0",
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="e",
            height=80,
            fg_color="#1e1e1e",
            text_color="#ffffff",
            corner_radius=12,
        )
        self._display.grid(
            row=1, column=0, columnspan=2, padx=12, pady=(0, 6), sticky="nsew"
        )

        # -- Buttons -------------------------------------------------------
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=12, pady=6, sticky="nsew")

        for r, row in enumerate(_BUTTON_LAYOUT):
            btn_frame.grid_rowconfigure(r, weight=1)
            for c, label in enumerate(row):
                if not label:
                    continue
                btn_frame.grid_columnconfigure(c, weight=1)
                btn = ctk.CTkButton(
                    btn_frame,
                    text=label,
                    font=ctk.CTkFont(size=18),
                    height=52,
                    fg_color=_btn_color(label),
                    command=lambda l=label: self._on_calc_button(l),
                )
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        # -- History sidebar (click an entry to reuse its expression) ------
        sidebar = ctk.CTkFrame(tab, width=200, corner_radius=12)
        sidebar.grid(row=2, column=1, padx=(0, 12), pady=6, sticky="nsew")
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(1, weight=1)

        side_header = ctk.CTkFrame(sidebar, fg_color="transparent")
        side_header.grid(row=0, column=0, padx=8, pady=(8, 4), sticky="ew")
        side_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            side_header,
            text="🕘 Historial",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            side_header,
            text="🗑",
            font=ctk.CTkFont(size=13),
            width=30,
            height=26,
            fg_color="#b3413a",
            command=self._clear_history,
        ).grid(row=0, column=1)

        self._history_list = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        self._history_list.grid(row=1, column=0, padx=6, pady=(0, 8), sticky="nsew")
        self._history_list.grid_columnconfigure(0, weight=1)
        self._refresh_history()

        # -- Keyboard bindings (on the main window, guarded by active tab) -
        self.bind("<Return>", lambda _e: self._calc_evaluate())
        self.bind("<KP_Enter>", lambda _e: self._calc_evaluate())
        self.bind("<Escape>", lambda _e: self._calc_clear())
        self.bind("<BackSpace>", lambda _e: self._calc_backspace())
        for char in "0123456789.+-*/()^%":
            self.bind(char, lambda e, c=char: self._calc_append(c))
        for letter in "abcdefghijklmnopqrstuvwxyz":
            self.bind(letter, lambda e, c=letter: self._calc_append(c))
            self.bind(letter.upper(), lambda e, c=letter.upper(): self._calc_append(c))

    # --- Calculator helpers -------------------------------------------

    def _refresh_history(self) -> None:
        """Rebuild the history sidebar (newest first, click to reuse)."""
        for w in self._history_list.winfo_children():
            w.destroy()

        entries = self._history.entries
        if not entries:
            ctk.CTkLabel(
                self._history_list,
                text="Sin operaciones aún",
                font=ctk.CTkFont(size=12),
                text_color="#888888",
            ).grid(row=0, column=0, pady=10)
            return

        for i, entry in enumerate(entries):
            btn = ctk.CTkButton(
                self._history_list,
                text=entry.label(30),
                anchor="w",
                font=ctk.CTkFont(size=12, family="Consolas"),
                height=34,
                fg_color="#3a3a3a" if i % 2 == 0 else "#454545",
                hover_color="#4a4a5a",
                command=lambda e=entry: self._use_history_entry(e),
            )
            btn.grid(row=i, column=0, pady=2, sticky="ew")

    def _use_history_entry(self, entry: HistoryEntry) -> None:
        """Put a past expression back into the display for editing/reuse."""
        self._expression = entry.expression
        self._display.configure(text=self._expression or "0", text_color="#ffffff")

    def _clear_history(self) -> None:
        self._history.clear()
        self._refresh_history()

    def _toggle_angle_mode(self) -> None:
        """Switch trig functions between degrees and radians."""
        new_mode = ANGLE_RAD if self._calc.angle_mode == ANGLE_DEG else ANGLE_DEG
        self._calc.angle_mode = new_mode
        is_deg = new_mode == ANGLE_DEG
        self._angle_btn.configure(
            text=f"Angle: {new_mode.upper()}",
            fg_color="#3a3a3a" if is_deg else "#3a6ea5",
        )
        self._angle_hint.configure(
            text="trig in degrees" if is_deg else "trig in radians"
        )

    def _on_this_tab(self, name: str) -> bool:
        """True when *name* is the currently visible tab.

        Global keyboard bindings fire no matter where the focus is, so every
        handler checks this first — typing in the notepad must not append to
        the calculator, and Enter in the base converter must not evaluate it.
        """
        return self._tabs.get() == name

    def _on_calc_button(self, label: str) -> None:
        if label == "C":
            self._calc_clear()
        elif label == "←":
            self._calc_backspace()
        elif label == "=":
            self._calc_evaluate()
        elif label in _BTN_TEXT:
            self._calc_append(_BTN_TEXT[label])
        else:
            self._calc_append(label)

    def _calc_append(self, char: str) -> None:
        if not self._on_this_tab(_TAB_CALC):
            return
        self._expression += char
        self._display.configure(text=self._expression, text_color="#ffffff")

    def _calc_clear(self) -> None:
        if not self._on_this_tab(_TAB_CALC):
            return
        self._expression = ""
        self._display.configure(text="0", text_color="#ffffff")

    def _calc_backspace(self) -> None:
        if not self._on_this_tab(_TAB_CALC):
            return
        self._expression = self._expression[:-1]
        self._display.configure(text=self._expression or "0", text_color="#ffffff")

    def _calc_evaluate(self) -> None:
        if not self._on_this_tab(_TAB_CALC) or not self._expression:
            return
        expression = self._expression
        try:
            result = self._calc.evaluate(expression)
        except CalculatorError as exc:
            # Show the real reason ("División entre cero", "Se esperaba ')'", …)
            # instead of a bare "Error", truncated so it fits the display.
            message = str(exc).strip() or "Error"
            if len(message) > 52:
                message = message[:49] + "…"
            self._display.configure(text=f"✗ {message}", text_color="#e06c75")
            self._expression = ""
            return
        formatted = self._fmt(result)
        self._display.configure(text=formatted, text_color="#2fa572")
        self._expression = formatted
        self._history.add(expression, formatted)
        self._refresh_history()

    @staticmethod
    def _fmt(value: float) -> str:
        # Core already rejects non-finite results; this is defense in depth
        # so a stray inf/NaN can never crash the display with OverflowError.
        if not math.isfinite(value):
            if math.isnan(value):
                return "NaN"
            return "∞" if value > 0 else "-∞"
        if value == int(value):
            return str(int(value))
        return f"{value:.10g}"

    # ------------------------------------------------------------------ #
    #  2. BASE CONVERTER                                                  #
    # ------------------------------------------------------------------ #

    def _build_base_converter_tab(self) -> None:
        tab = self._tab_base
        tab.grid_columnconfigure(0, weight=1)

        self._base_vars: dict[str, ctk.StringVar] = {}
        self._base_entries: dict[str, ctk.CTkEntry] = {}
        self._base_syncing = False  # re-entrancy guard for the cross-field traces

        for i, key in enumerate(_BASE_KEYS):
            tab.grid_rowconfigure(i, weight=0)

            row_frame = ctk.CTkFrame(tab, fg_color="transparent")
            row_frame.grid(row=i, column=0, padx=12, pady=4, sticky="nsew")
            row_frame.grid_columnconfigure(1, weight=1)

            lbl = ctk.CTkLabel(
                row_frame,
                text=_BASE_LABELS[key],
                font=ctk.CTkFont(size=14, weight="bold"),
                width=90,
                anchor="w",
            )
            lbl.grid(row=0, column=0, padx=(0, 8), sticky="w")

            var = ctk.StringVar()
            entry = ctk.CTkEntry(
                row_frame,
                textvariable=var,
                font=ctk.CTkFont(size=16, family="Consolas"),
                height=40,
                corner_radius=8,
            )
            entry.grid(row=0, column=1, sticky="nsew")

            # Copy button
            copy_btn = ctk.CTkButton(
                row_frame,
                text="📋",
                font=ctk.CTkFont(size=14),
                width=36,
                height=36,
                fg_color="#3a3a3a",
                command=lambda k=key: self._copy_base_field(k),
            )
            copy_btn.grid(row=0, column=2, padx=(6, 0))

            self._base_vars[key] = var
            self._base_entries[key] = entry

            # Bind real-time conversion
            var.trace_add("write", lambda *_a, k=key: self._on_base_input(k))

    def _on_base_input(self, source_key: str) -> None:
        """Convert from whichever field the user is typing into.

        Writes to the other three fields fire *their* traces as well (Tk fires
        write traces even when the value doesn't change). The
        _base_syncing guard makes those nested callbacks no-ops, so a single
        keystroke does exactly one conversion pass and the field being
        edited is never clobbered with "—" by its own cascade.
        """
        if self._base_syncing:
            return
        self._base_syncing = True
        try:
            raw = self._base_vars[source_key].get().strip()
            if not raw:
                for k in _BASE_KEYS:
                    if k != source_key:
                        self._base_vars[k].set("")
                return

            try:
                results = convert(raw, _BASE_RADIX[source_key])
            except BaseConverterError:
                for k in _BASE_KEYS:
                    if k != source_key:
                        self._base_vars[k].set("—")
                return

            # Update the other three fields with the conversion results
            for k in _BASE_KEYS:
                if k != source_key:
                    self._base_vars[k].set(results[k])
        finally:
            self._base_syncing = False

    def _copy_base_field(self, key: str) -> None:
        """Copy the value of a base-converter field to the clipboard."""
        value = self._base_vars[key].get()
        if value:
            self.clipboard_clear()
            self.clipboard_append(value)
            self._flash_copy_button(key)

    def _flash_copy_button(self, key: str) -> None:
        """Briefly show a ✓ feedback on the copy button."""
        idx = _BASE_KEYS.index(key)
        # Find the copy button widget — it's the last child in the row frame
        tab = self._tab_base
        row_frames = [w for w in tab.winfo_children() if isinstance(w, ctk.CTkFrame)]
        if idx < len(row_frames):
            btns = [w for w in row_frames[idx].winfo_children() if isinstance(w, ctk.CTkButton)]
            if btns:
                btn = btns[-1]
                original = btn.cget("text")
                btn.configure(text="✓", fg_color="#2fa572")
                self.after(600, lambda: btn.configure(text=original, fg_color="#3a3a3a"))

    # ------------------------------------------------------------------ #
    #  3. ASCII TABLE                                                     #
    # ------------------------------------------------------------------ #

    def _build_ascii_table_tab(self) -> None:
        tab = self._tab_ascii
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Search bar
        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="nsew")
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_frame, text="🔍", font=ctk.CTkFont(size=16)
        ).grid(row=0, column=0, padx=(0, 6))

        self._ascii_search_var = ctk.StringVar()
        self._ascii_search_var.trace_add("write", lambda *_a: self._refresh_ascii_table())
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self._ascii_search_var,
            placeholder_text="Search by dec, hex, char, or name…",
            font=ctk.CTkFont(size=14),
            height=36,
        )
        search_entry.grid(row=0, column=1, sticky="nsew")

        # Table (scrollable frame with header + rows)
        self._ascii_scroll = ctk.CTkScrollableFrame(tab, fg_color=_DARK_BG, corner_radius=8)
        self._ascii_scroll.grid(row=1, column=0, padx=12, pady=(4, 10), sticky="nsew")
        self._ascii_scroll.grid_columnconfigure(4, weight=1)

        self._refresh_ascii_table()

    def _refresh_ascii_table(self) -> None:
        """Rebuild the ASCII table rows inside the scrollable frame."""
        # Clear existing widgets
        for w in self._ascii_scroll.winfo_children():
            w.destroy()

        query = self._ascii_search_var.get()
        rows = search_table(query) if query else generate_table()

        # Header
        for c, col in enumerate(_TABLE_COLUMNS):
            ctk.CTkLabel(
                self._ascii_scroll,
                text=col,
                font=ctk.CTkFont(size=13, weight="bold"),
                width=_COL_WIDTHS[col],
                anchor="center",
            ).grid(row=0, column=c, padx=2, pady=(4, 2))

        # Rows
        for r, row in enumerate(rows, start=1):
            bg = "#2a2a2a" if r % 2 == 0 else "transparent"
            for c, col in enumerate(_TABLE_COLUMNS):
                val = row[col]
                lbl = ctk.CTkLabel(
                    self._ascii_scroll,
                    text=val,
                    font=ctk.CTkFont(size=13, family="Consolas"),
                    width=_COL_WIDTHS[col],
                    anchor="center",
                    fg_color=bg,
                    corner_radius=2,
                )
                lbl.grid(row=r, column=c, padx=1, pady=1)

    # ------------------------------------------------------------------ #
    #  4. NOTEPAD                                                         #
    # ------------------------------------------------------------------ #

    def _build_notepad_tab(self) -> None:
        tab = self._tab_notepad
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Toolbar
        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.grid(row=0, column=0, padx=12, pady=(8, 4), sticky="ew")

        ctk.CTkButton(
            toolbar, text="💾 Save", font=ctk.CTkFont(size=13),
            width=80, height=30, fg_color="#2fa572",
            command=self._notepad_save,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            toolbar, text="📂 Open", font=ctk.CTkFont(size=13),
            width=80, height=30, fg_color="#3a6ea5",
            command=self._notepad_open,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            toolbar, text="🗑 Clear", font=ctk.CTkFont(size=13),
            width=80, height=30, fg_color="#b3413a",
            command=self._notepad_clear,
        ).pack(side="left")

        self._notepad_status = ctk.CTkLabel(
            toolbar, text="", font=ctk.CTkFont(size=12),
            text_color="#888888",
        )
        self._notepad_status.pack(side="right")

        ctk.CTkButton(
            toolbar, text="↩ Undo", font=ctk.CTkFont(size=13),
            width=80, height=30, fg_color="#5a3a8a",
            command=self._notepad_undo,
        ).pack(side="left", padx=(12, 6))

        ctk.CTkButton(
            toolbar, text="↪ Redo", font=ctk.CTkFont(size=13),
            width=80, height=30, fg_color="#5a3a8a",
            command=self._notepad_redo,
        ).pack(side="left")

        # Text editor (undo=True enables the built-in undo stack)
        self._notepad_text = ctk.CTkTextbox(
            tab,
            font=ctk.CTkFont(size=14, family="Consolas"),
            corner_radius=8,
            wrap="word",
            undo=True,
        )
        self._notepad_text.grid(row=1, column=0, padx=12, pady=(4, 10), sticky="nsew")
        self._notepad_text.insert("1.0", "Start typing here…")
        self._notepad_text.edit_reset()  # clear the undo history for the initial text
        self._notepad_text.edit_modified(False)
        self._notepad_file_path: str | None = None

        # Keyboard shortcuts: Ctrl+Z = undo, Ctrl+Y / Ctrl+Shift+Z = redo
        self.bind("<Control-z>", lambda _e: self._notepad_undo())
        self.bind("<Control-y>", lambda _e: self._notepad_redo())
        self.bind("<Control-Shift-Z>", lambda _e: self._notepad_redo())

    def _notepad_save(self) -> None:
        """Save notepad content to a file via dialog."""
        from tkinter import filedialog

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="notes.txt",
        )
        if not path:
            return
        content = self._notepad_text.get("1.0", "end-1c")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self._notepad_file_path = path
        self._notepad_status.configure(text=f"Saved: {path}")

    def _notepad_open(self) -> None:
        """Open a text file into the notepad."""
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self._notepad_text.delete("1.0", "end")
        self._notepad_text.insert("1.0", content)
        self._notepad_file_path = path
        self._notepad_status.configure(text=f"Opened: {path}")

    def _notepad_clear(self) -> None:
        """Clear the notepad."""
        self._notepad_text.delete("1.0", "end")
        self._notepad_text.edit_reset()
        self._notepad_text.edit_modified(False)
        self._notepad_file_path = None
        self._notepad_status.configure(text="Cleared")

    def _notepad_undo(self) -> None:
        """Undo the last edit in the notepad (only while its tab is open)."""
        if not self._on_this_tab(_TAB_NOTEPAD):
            return
        try:
            self._notepad_text.edit_undo()
            self._notepad_status.configure(text="Undo")
        except tk.TclError:
            pass  # nothing to undo

    def _notepad_redo(self) -> None:
        """Redo the last undone edit in the notepad (only while its tab is open)."""
        if not self._on_this_tab(_TAB_NOTEPAD):
            return
        try:
            self._notepad_text.edit_redo()
            self._notepad_status.configure(text="Redo")
        except tk.TclError:
            pass  # nothing to redo

    # ------------------------------------------------------------------ #
    #  THEME TOGGLE                                                       #
    # ------------------------------------------------------------------ #

    def _toggle_theme(self) -> None:
        """Switch between dark and light mode."""
        self._is_dark = not self._is_dark
        mode = "dark" if self._is_dark else "light"
        ctk.set_appearance_mode(mode)
        self._theme_btn.configure(
            text="🌙 Dark" if self._is_dark else "☀️ Light",
        )


# ========================================================================
#  ENTRY POINT
# ========================================================================

def main() -> None:
    app = EverythingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
