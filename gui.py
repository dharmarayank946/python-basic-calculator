"""Calculator Pro — Studio Obsidian Edition.
=============================================
A modern, precision-engineered desktop calculator featuring an authentic
Studio Obsidian hardware aesthetic, OLED display bezel, and tactile controls.

Features:
- Form Factor: Compact, ergonomic desktop tool (Standard & Scientific modes).
- Display: Deep OLED black panel with expression preview and large high-contrast digits.
- Precision Palette: Matte Obsidian (#121214), Charcoal Keypad (#27272A), Electric Amber operators (#F59E0B), Emerald Equals (#10B981), and Cyber Indigo scientific tools (#1E1B4B).
- Mode Segmented Control: Toggle between Standard (clean 4x5) and Scientific (extended 6x4).
- Slide-out History Ledger with one-click recall and clear options.
- One-touch Copy Result with visual feedback toast.
- Keyboard Bindings: Full desktop keyboard ergonomics.
- Safe AST evaluation engine (zero eval).
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox

from calc_engine import (
    SafeExpressionEvaluator,
    safe_square_root,
    safe_reciprocal,
    safe_percentage,
    safe_square,
    format_display_number,
    CalculationHistory,
)


# =============================================================================
# Studio Obsidian Palette (Dark, Metallic, Tactile)
# =============================================================================
COLOR_BG = "#121214"            # Deep obsidian chassis
COLOR_BEZEL = "#1C1C20"         # Outer metal rim / divider
COLOR_OLED_BG = "#08080A"       # OLED pitch-black screen
COLOR_OLED_BORDER = "#27272A"   # Screen perimeter border

COLOR_TEXT_MAIN = "#FAFAFA"     # Crisp illuminated white
COLOR_TEXT_MUTED = "#71717A"    # Subdued indicator gray
COLOR_CYAN_ACCENT = "#38BDF8"   # Cyber cyan for scientific operators

# Keypad Colors
COLOR_NUM_BG = "#222226"        # Charcoal slate numeric key
COLOR_NUM_HOVER = "#323238"     # Hover state
COLOR_NUM_TEXT = "#F4F4F5"      # High-contrast white number

COLOR_OP_BG = "#D97706"         # Electric Amber operator
COLOR_OP_HOVER = "#F59E0B"      # Glowing amber hover
COLOR_OP_TEXT = "#FFFFFF"       # White operator icon

COLOR_EQUALS_BG = "#059669"     # Emerald Green equals
COLOR_EQUALS_HOVER = "#10B981"  # Bright emerald hover
COLOR_EQUALS_TEXT = "#FFFFFF"   # White text

COLOR_CLEAR_BG = "#450A0A"      # Deep matte crimson
COLOR_CLEAR_HOVER = "#7F1D1D"   # Crimson hover
COLOR_CLEAR_TEXT = "#FECACA"    # Pale rose text

COLOR_FN_BG = "#1E1B4B"         # Deep Indigo scientific key
COLOR_FN_HOVER = "#312E81"      # Indigo hover
COLOR_FN_TEXT = "#93C5FD"       # Soft ice blue text

COLOR_TOAST_OK_BG = "#064E3B"   # Status OK
COLOR_TOAST_OK_FG = "#6EE7B7"
COLOR_TOAST_ERR_BG = "#7F1D1D"  # Status Error
COLOR_TOAST_ERR_FG = "#FCA5A5"


class CalculatorProGUI:
    """Studio Obsidian Desktop Calculator Interface."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculator Pro ✦ Studio Obsidian")
        self.root.geometry("420x620")
        self.root.minsize(380, 560)
        self.root.configure(bg=COLOR_BG)

        # Elevate window on startup
        self._bring_to_front()

        # Engine & State
        self.evaluator = SafeExpressionEvaluator()
        self.history = CalculationHistory()

        self.current_expression = ""
        self.active_input = "0"
        self.is_new_calculation = True
        self.mode = "scientific"  # 'standard' or 'scientific'
        self.show_history_panel = False

        # Build UI
        self._build_header_and_mode_bar()
        self._build_main_container()

        # Keyboard Bindings
        self._bind_keyboard()

    def _bring_to_front(self):
        """Elevate window gracefully on launch."""
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after(400, lambda: self.root.attributes("-topmost", False))
            self.root.focus_force()
        except Exception:
            pass

    # =========================================================================
    # Header & Mode Segmented Control
    # =========================================================================
    def _build_header_and_mode_bar(self):
        """Construct top toolbar with segmented mode pills and history toggle."""
        toolbar = tk.Frame(self.root, bg=COLOR_BG, padx=16, pady=10)
        toolbar.pack(fill=tk.X)

        # Left: Compact Branding
        brand_box = tk.Frame(toolbar, bg=COLOR_BG)
        brand_box.pack(side=tk.LEFT)

        tk.Label(
            brand_box,
            text="🧮 CALCULATOR PRO",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_TEXT_MAIN,
            bg=COLOR_BG
        ).pack(side=tk.LEFT)

        # Center/Right: Mode Segmented Control
        mode_pill_frame = tk.Frame(toolbar, bg=COLOR_BEZEL, padx=2, pady=2)
        mode_pill_frame.pack(side=tk.RIGHT)

        self.std_btn = tk.Button(
            mode_pill_frame,
            text="Standard",
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_BEZEL,
            fg=COLOR_TEXT_MUTED,
            activebackground=COLOR_NUM_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            bd=0,
            command=lambda: self.switch_mode("standard")
        )
        self.std_btn.pack(side=tk.LEFT)

        self.sci_btn = tk.Button(
            mode_pill_frame,
            text="Scientific",
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_NUM_BG,
            fg=COLOR_TEXT_MAIN,
            activebackground=COLOR_NUM_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            bd=0,
            command=lambda: self.switch_mode("scientific")
        )
        self.sci_btn.pack(side=tk.LEFT)

        self.hist_btn = tk.Button(
            mode_pill_frame,
            text="🕒 History",
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_BEZEL,
            fg=COLOR_TEXT_MUTED,
            activebackground=COLOR_NUM_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            bd=0,
            command=self.toggle_history_drawer
        )
        self.hist_btn.pack(side=tk.LEFT)

        # Subtle Status Toast Bar
        self.toast_label = tk.Label(
            self.root,
            text="Precision Audio/Math Ready",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_BG,
            pady=1
        )
        self.toast_label.pack(fill=tk.X, padx=16)

    def show_toast(self, text: str, is_error: bool = False, ms: int = 2200):
        """Show tactical status toast."""
        bg = COLOR_TOAST_ERR_BG if is_error else COLOR_TOAST_OK_BG
        fg = COLOR_TOAST_ERR_FG if is_error else COLOR_TOAST_OK_FG
        self.toast_label.configure(text=f"{'⚠️ ' if is_error else '✔ '}{text}", bg=bg, fg=fg, font=("Segoe UI", 8, "bold"))
        self.root.after(ms, lambda: self.toast_label.configure(text="Precision Math Ready", bg=COLOR_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 8)))

    def switch_mode(self, new_mode: str):
        """Toggle between Standard and Scientific keypad layout."""
        self.mode = new_mode
        if new_mode == "standard":
            self.std_btn.configure(bg=COLOR_NUM_BG, fg=COLOR_TEXT_MAIN)
            self.sci_btn.configure(bg=COLOR_BEZEL, fg=COLOR_TEXT_MUTED)
        else:
            self.sci_btn.configure(bg=COLOR_NUM_BG, fg=COLOR_TEXT_MAIN)
            self.std_btn.configure(bg=COLOR_BEZEL, fg=COLOR_TEXT_MUTED)

        self._rebuild_keypad()

    # =========================================================================
    # Main Container: OLED Display + Keypad + Slide-out History
    # =========================================================================
    def _build_main_container(self):
        """Create split layout between calculator chassis and history drawer."""
        self.split_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.split_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(4, 16))

        # Calculator Column
        self.calc_body = tk.Frame(self.split_frame, bg=COLOR_BG)
        self.calc_body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_oled_screen(self.calc_body)

        self.keypad_container = tk.Frame(self.calc_body, bg=COLOR_BG)
        self.keypad_container.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self._rebuild_keypad()

        # History Ledger Drawer (initially unmapped)
        self.history_drawer = tk.Frame(
            self.split_frame,
            bg=COLOR_BEZEL,
            highlightbackground=COLOR_OLED_BORDER,
            highlightthickness=1,
            width=220
        )
        self._build_history_drawer_contents()

    def _build_oled_screen(self, parent: tk.Frame):
        """Construct deep pitch-black OLED display card with glowing bezel."""
        oled_card = tk.Frame(
            parent,
            bg=COLOR_OLED_BG,
            highlightbackground=COLOR_OLED_BORDER,
            highlightthickness=1,
            padx=16,
            pady=14
        )
        oled_card.pack(fill=tk.X)

        # Expression Preview Line
        self.preview_label = tk.Label(
            oled_card,
            text="",
            font=("Consolas", 11),
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_OLED_BG,
            anchor="e"
        )
        self.preview_label.pack(fill=tk.X)

        # Primary Digital Readout
        self.result_label = tk.Label(
            oled_card,
            text="0",
            font=("Segoe UI", 36, "bold"),
            fg=COLOR_TEXT_MAIN,
            bg=COLOR_OLED_BG,
            anchor="e"
        )
        self.result_label.pack(fill=tk.X, pady=(2, 6))

        # Bottom Bar of Screen: Actions
        screen_bar = tk.Frame(oled_card, bg=COLOR_OLED_BG)
        screen_bar.pack(fill=tk.X)

        copy_btn = tk.Button(
            screen_bar,
            text="📋 Copy",
            font=("Segoe UI", 8),
            bg=COLOR_BEZEL,
            fg=COLOR_TEXT_MUTED,
            activebackground=COLOR_NUM_HOVER,
            activeforeground=COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            padx=6,
            pady=2,
            cursor="hand2",
            bd=0,
            command=self.copy_result_to_clipboard
        )
        copy_btn.pack(side=tk.LEFT)

        ce_btn = tk.Button(
            screen_bar,
            text="CE",
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_CLEAR_BG,
            fg=COLOR_CLEAR_TEXT,
            activebackground=COLOR_CLEAR_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            bd=0,
            command=self.clear_entry
        )
        ce_btn.pack(side=tk.RIGHT)

        c_btn = tk.Button(
            screen_bar,
            text="C",
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_CLEAR_BG,
            fg=COLOR_CLEAR_TEXT,
            activebackground=COLOR_CLEAR_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            bd=0,
            command=self.clear_all
        )
        c_btn.pack(side=tk.RIGHT, padx=(0, 6))

        back_btn = tk.Button(
            screen_bar,
            text="⌫",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_BEZEL,
            fg=COLOR_TEXT_MAIN,
            activebackground=COLOR_NUM_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=1,
            cursor="hand2",
            bd=0,
            command=self.backspace
        )
        back_btn.pack(side=tk.RIGHT, padx=(0, 6))

    def _rebuild_keypad(self):
        """Construct the tactile keypad grid according to active mode."""
        for w in self.keypad_container.winfo_children():
            w.destroy()

        if self.mode == "scientific":
            rows = 6
            cols = 4
            layout = [
                # Row 0: Scientific functions
                (0, 0, "(", "fn", lambda: self.append_character("(")),
                (0, 1, ")", "fn", lambda: self.append_character(")")),
                (0, 2, "x²", "fn", self.apply_square),
                (0, 3, "√", "fn", self.apply_sqrt),

                # Row 1: Utilities
                (1, 0, "1/x", "fn", self.apply_reciprocal),
                (1, 1, "%", "fn", lambda: self.append_operator("%")),
                (1, 2, "^", "fn", lambda: self.append_operator("^")),
                (1, 3, "÷", "op", lambda: self.append_operator("÷")),

                # Row 2: 7, 8, 9, ×
                (2, 0, "7", "num", lambda: self.append_digit("7")),
                (2, 1, "8", "num", lambda: self.append_digit("8")),
                (2, 2, "9", "num", lambda: self.append_digit("9")),
                (2, 3, "×", "op", lambda: self.append_operator("×")),

                # Row 3: 4, 5, 6, −
                (3, 0, "4", "num", lambda: self.append_digit("4")),
                (3, 1, "5", "num", lambda: self.append_digit("5")),
                (3, 2, "6", "num", lambda: self.append_digit("6")),
                (3, 3, "−", "op", lambda: self.append_operator("−")),

                # Row 4: 1, 2, 3, +
                (4, 0, "1", "num", lambda: self.append_digit("1")),
                (4, 1, "2", "num", lambda: self.append_digit("2")),
                (4, 2, "3", "num", lambda: self.append_digit("3")),
                (4, 3, "+", "op", lambda: self.append_operator("+")),

                # Row 5: ±, 0, ., =
                (5, 0, "±", "fn", self.toggle_sign),
                (5, 1, "0", "num", lambda: self.append_digit("0")),
                (5, 2, ".", "num", self.append_decimal),
                (5, 3, "=", "equals", self.calculate_result),
            ]
        else:
            # Standard Mode (5 rows x 4 cols)
            rows = 5
            cols = 4
            layout = [
                # Row 0: Utilities
                (0, 0, "%", "fn", lambda: self.append_operator("%")),
                (0, 1, "√", "fn", self.apply_sqrt),
                (0, 2, "x²", "fn", self.apply_square),
                (0, 3, "÷", "op", lambda: self.append_operator("÷")),

                # Row 1: 7, 8, 9, ×
                (1, 0, "7", "num", lambda: self.append_digit("7")),
                (1, 1, "8", "num", lambda: self.append_digit("8")),
                (1, 2, "9", "num", lambda: self.append_digit("9")),
                (1, 3, "×", "op", lambda: self.append_operator("×")),

                # Row 2: 4, 5, 6, −
                (2, 0, "4", "num", lambda: self.append_digit("4")),
                (2, 1, "5", "num", lambda: self.append_digit("5")),
                (2, 2, "6", "num", lambda: self.append_digit("6")),
                (2, 3, "−", "op", lambda: self.append_operator("−")),

                # Row 3: 1, 2, 3, +
                (3, 0, "1", "num", lambda: self.append_digit("1")),
                (3, 1, "2", "num", lambda: self.append_digit("2")),
                (3, 2, "3", "num", lambda: self.append_digit("3")),
                (3, 3, "+", "op", lambda: self.append_operator("+")),

                # Row 4: ±, 0, ., =
                (4, 0, "±", "fn", self.toggle_sign),
                (4, 1, "0", "num", lambda: self.append_digit("0")),
                (4, 2, ".", "num", self.append_decimal),
                (4, 3, "=", "equals", self.calculate_result),
            ]

        for r in range(rows):
            self.keypad_container.rowconfigure(r, weight=1, uniform="krow")
        for c in range(cols):
            self.keypad_container.columnconfigure(c, weight=1, uniform="kcol")

        for r, c, label, style, cmd in layout:
            self._create_tactile_button(self.keypad_container, r, c, label, style, cmd)

    def _create_tactile_button(self, parent: tk.Frame, r: int, c: int, label: str, style: str, cmd):
        """Construct button with metallic contour and hover lighting."""
        if style == "num":
            bg = COLOR_NUM_BG
            hover = COLOR_NUM_HOVER
            fg = COLOR_NUM_TEXT
            font = ("Segoe UI", 15, "bold")
        elif style == "op":
            bg = COLOR_OP_BG
            hover = COLOR_OP_HOVER
            fg = COLOR_OP_TEXT
            font = ("Segoe UI", 16, "bold")
        elif style == "equals":
            bg = COLOR_EQUALS_BG
            hover = COLOR_EQUALS_HOVER
            fg = COLOR_EQUALS_TEXT
            font = ("Segoe UI", 18, "bold")
        else:  # "fn"
            bg = COLOR_FN_BG
            hover = COLOR_FN_HOVER
            fg = COLOR_FN_TEXT
            font = ("Segoe UI", 12, "bold")

        btn = tk.Button(
            parent,
            text=label,
            font=font,
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=cmd
        )
        btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

        btn.bind("<Enter>", lambda e, b=btn, h=hover: b.configure(bg=h))
        btn.bind("<Leave>", lambda e, b=btn, orig=bg: b.configure(bg=orig))

    # =========================================================================
    # Slide-Out History Drawer
    # =========================================================================
    def _build_history_drawer_contents(self):
        """Construct history drawer widgets."""
        h_bar = tk.Frame(self.history_drawer, bg=COLOR_BEZEL, padx=10, pady=8)
        h_bar.pack(fill=tk.X)

        tk.Label(h_bar, text="LEDGER", font=("Consolas", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BEZEL).pack(side=tk.LEFT)

        tk.Button(
            h_bar,
            text="Clear",
            font=("Segoe UI", 8),
            bg=COLOR_CLEAR_BG,
            fg=COLOR_CLEAR_TEXT,
            relief=tk.FLAT,
            padx=6,
            pady=1,
            cursor="hand2",
            bd=0,
            command=self.clear_history_log
        ).pack(side=tk.RIGHT)

        self.hist_canvas = tk.Canvas(self.history_drawer, bg=COLOR_OLED_BG, highlightthickness=0, bd=0)
        self.hist_scrollbar = ttk.Scrollbar(self.history_drawer, orient=tk.VERTICAL, command=self.hist_canvas.yview)
        self.hist_list_frame = tk.Frame(self.hist_canvas, bg=COLOR_OLED_BG)

        self.hist_list_frame.bind("<Configure>", lambda e: self.hist_canvas.configure(scrollregion=self.hist_canvas.bbox("all")))
        self.hist_win = self.hist_canvas.create_window((0, 0), window=self.hist_list_frame, anchor="nw")

        def _on_hist_cfg(e):
            self.hist_canvas.itemconfig(self.hist_win, width=e.width)

        self.hist_canvas.bind("<Configure>", _on_hist_cfg)
        self.hist_canvas.configure(yscrollcommand=self.hist_scrollbar.set)

        self.hist_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.hist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def toggle_history_drawer(self):
        """Toggle slide-out ledger on the right."""
        self.show_history_panel = not self.show_history_panel
        if self.show_history_panel:
            self.root.geometry("640x620")
            self.history_drawer.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
            self.hist_btn.configure(bg=COLOR_OP_BG, fg="#FFFFFF")
            self._render_history_list()
        else:
            self.history_drawer.pack_forget()
            self.root.geometry("420x620")
            self.hist_btn.configure(bg=COLOR_BEZEL, fg=COLOR_TEXT_MUTED)

    def _render_history_list(self):
        """Populate history entries."""
        for w in self.hist_list_frame.winfo_children():
            w.destroy()

        entries = self.history.get_entries()
        if not entries:
            tk.Label(
                self.hist_list_frame,
                text="No logs recorded.\nCalculate to log.",
                font=("Segoe UI", 9, "italic"),
                fg=COLOR_TEXT_MUTED,
                bg=COLOR_OLED_BG,
                pady=20,
                justify=tk.CENTER
            ).pack(fill=tk.X)
            return

        for item in entries:
            c = tk.Frame(self.hist_list_frame, bg=COLOR_BEZEL, padx=8, pady=6, cursor="hand2")
            c.pack(fill=tk.X, padx=4, pady=3)

            tk.Label(c, text=item["expression"], font=("Consolas", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_BEZEL, anchor="e").pack(fill=tk.X)
            tk.Label(c, text=f"= {item['result']}", font=("Consolas", 11, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BEZEL, anchor="e").pack(fill=tk.X)

            c.bind("<Button-1>", lambda e, v=item["result"]: self._recall_history_result(v))

    def _recall_history_result(self, val: str):
        """Recall entry value to active screen."""
        self.active_input = str(val)
        self.is_new_calculation = True
        self._update_display()
        self.show_toast(f"Recalled '{val}'")

    def clear_history_log(self):
        """Clear ledger logs."""
        self.history.clear()
        self._render_history_list()
        self.show_toast("Ledger cleared")

    # =========================================================================
    # Math & Event Operations
    # =========================================================================
    def append_digit(self, digit: str):
        if self.is_new_calculation:
            self.active_input = digit
            self.is_new_calculation = False
        else:
            if self.active_input == "0":
                self.active_input = digit
            else:
                self.active_input += digit
        self._update_display()

    def append_decimal(self):
        if self.is_new_calculation:
            self.active_input = "0."
            self.is_new_calculation = False
        elif "." not in self.active_input:
            self.active_input += "."
        self._update_display()

    def append_operator(self, op: str):
        if self.current_expression and self.is_new_calculation:
            self.current_expression = self.current_expression.rstrip("+-×÷^% ") + f" {op} "
        else:
            self.current_expression += f"{self.active_input} {op} "

        self.is_new_calculation = True
        self._update_display()

    def append_character(self, char: str):
        if self.is_new_calculation:
            self.active_input = char
            self.is_new_calculation = False
        else:
            self.active_input += char
        self._update_display()

    def toggle_sign(self):
        try:
            val = float(self.active_input)
            self.active_input = format_display_number(-val)
            self._update_display()
        except ValueError:
            pass

    def apply_sqrt(self):
        res = safe_square_root(self.active_input)
        if isinstance(res, str):
            self.show_toast(res, is_error=True)
            self.active_input = "0"
        else:
            formatted = format_display_number(res)
            self.history.add_entry(f"√({self.active_input})", formatted)
            self.active_input = formatted
            self.is_new_calculation = True
            self.show_toast("Square root computed")
            if self.show_history_panel:
                self._render_history_list()
        self._update_display()

    def apply_reciprocal(self):
        res = safe_reciprocal(self.active_input)
        if isinstance(res, str):
            self.show_toast(res, is_error=True)
        else:
            formatted = format_display_number(res)
            self.history.add_entry(f"1/({self.active_input})", formatted)
            self.active_input = formatted
            self.is_new_calculation = True
            self.show_toast("Reciprocal computed")
            if self.show_history_panel:
                self._render_history_list()
        self._update_display()

    def apply_square(self):
        res = safe_square(self.active_input)
        if isinstance(res, str):
            self.show_toast(res, is_error=True)
        else:
            formatted = format_display_number(res)
            self.history.add_entry(f"({self.active_input})²", formatted)
            self.active_input = formatted
            self.is_new_calculation = True
            self.show_toast("Square (x²) computed")
            if self.show_history_panel:
                self._render_history_list()
        self._update_display()

    def backspace(self):
        if self.is_new_calculation and not self.current_expression:
            self.active_input = "0"
            self._update_display()
            return

        if not self.is_new_calculation:
            if len(self.active_input) > 1:
                self.active_input = self.active_input[:-1]
            else:
                self.active_input = "0"
                self.is_new_calculation = True
        elif self.current_expression:
            trimmed = self.current_expression.strip()
            parts = trimmed.split()
            if len(parts) > 1:
                self.current_expression = " ".join(parts[:-2]) + (" " if len(parts) > 2 else "")
                self.active_input = parts[-2]
                self.is_new_calculation = False
            else:
                self.active_input = parts[0] if parts else "0"
                self.current_expression = ""
                self.is_new_calculation = False

        self._update_display()

    def clear_entry(self):
        self.active_input = "0"
        self.is_new_calculation = True
        self._update_display()

    def clear_all(self):
        self.current_expression = ""
        self.active_input = "0"
        self.is_new_calculation = True
        self.preview_label.configure(text="")
        self._update_display()
        self.show_toast("Cleared")

    def calculate_result(self):
        full_expr = (self.current_expression + self.active_input).strip()
        if not full_expr:
            return

        result = self.evaluator.evaluate(full_expr)
        if isinstance(result, str):
            self.show_toast(result, is_error=True)
            self.preview_label.configure(text=f"{full_expr} =")
            self.result_label.configure(text=result)
            self.is_new_calculation = True
            return

        formatted = format_display_number(result)
        self.history.add_entry(full_expr, formatted)
        if self.show_history_panel:
            self._render_history_list()

        self.preview_label.configure(text=f"{full_expr} =")
        self.active_input = formatted
        self.current_expression = ""
        self.is_new_calculation = True
        self._update_display(is_result=True)
        self.show_toast(f"= {formatted}")

    def copy_result_to_clipboard(self):
        val = self.active_input
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(val)
            self.show_toast(f"Copied '{val}' to clipboard!")
        except Exception:
            self.show_toast("Copy failed", is_error=True)

    def _update_display(self, is_result: bool = False):
        if is_result:
            text = self.active_input
        else:
            if self.current_expression:
                if self.is_new_calculation:
                    display_text = self.current_expression.strip()
                else:
                    display_text = f"{self.current_expression}{self.active_input}".strip()
                self.preview_label.configure(text=self.current_expression)
                text = display_text
            else:
                self.preview_label.configure(text="")
                text = self.active_input

        if len(text) > 16:
            self.result_label.configure(font=("Segoe UI", 18, "bold"), text=text)
        elif len(text) > 11:
            self.result_label.configure(font=("Segoe UI", 24, "bold"), text=text)
        else:
            self.result_label.configure(font=("Segoe UI", 36, "bold"), text=text)

    # =========================================================================
    # Keyboard Shortcuts
    # =========================================================================
    def _bind_keyboard(self):
        for d in "0123456789":
            self.root.bind(d, lambda e, digit=d: self.append_digit(digit))

        self.root.bind("+", lambda e: self.append_operator("+"))
        self.root.bind("-", lambda e: self.append_operator("−"))
        self.root.bind("*", lambda e: self.append_operator("×"))
        self.root.bind("/", lambda e: self.append_operator("÷"))
        self.root.bind("%", lambda e: self.append_operator("%"))
        self.root.bind("^", lambda e: self.append_operator("^"))

        self.root.bind("(", lambda e: self.append_character("("))
        self.root.bind(")", lambda e: self.append_character(")"))
        self.root.bind(".", lambda e: self.append_decimal())

        self.root.bind("<Return>", lambda e: self.calculate_result())
        self.root.bind("<KP_Enter>", lambda e: self.calculate_result())
        self.root.bind("=", lambda e: self.calculate_result())

        self.root.bind("<BackSpace>", lambda e: self.backspace())
        self.root.bind("<Delete>", lambda e: self.clear_entry())
        self.root.bind("<Escape>", lambda e: self.clear_all())
        self.root.bind("c", lambda e: self.clear_all())
        self.root.bind("C", lambda e: self.clear_all())

        self.root.bind("<Control-c>", lambda e: self.copy_result_to_clipboard())
        self.root.bind("<Control-C>", lambda e: self.copy_result_to_clipboard())


def launch_gui():
    """Launch the Studio Obsidian Desktop Calculator."""
    root = tk.Tk()
    app = CalculatorProGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
