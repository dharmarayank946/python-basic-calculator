# Calculator Pro — Desktop Calculator Application

> **Internship:** Python Development Internship — Week 1 Project Upgrade  
> **Core Focus:** Safe AST Mathematical Expression Evaluation, Dual-Line Display, Calculation History, Desktop Keyboard Ergonomics, and Standard Library Tkinter GUI.

---

## 1. Project Overview

**Calculator Pro** is an upgraded desktop calculator application developed as part of **Week 1 of the Python Development Internship**. It elevates the original basic arithmetic script into a desktop tool with a clean, light aesthetic inspired by **QuizUp Python Edition** and **WeatherWise V3**.

It retains the original beginner-friendly Python functions (`add`, `subtract`, `multiply`, `divide`) while providing a modern Tkinter interface with scientific helpers, collapsible history tracking, and strict protection against malicious code execution using an **AST (Abstract Syntax Tree)** safe evaluator.

---

## 2. Features

### User Interface & Experience
- **Dual-Line Calculation Display:** Shows the active expression preview line above and large typography for active entry/results below.
- **Modern Light Theme:** Soft blue and lavender accents, pure white elevated card surfaces, and responsive button hover transitions.
- **Collapsible Calculation History Drawer:** Slide-out drawer tracking up to 50 calculations with timestamps and one-click recall of past results back into the active input.
- **One-Click Copy Result:** Instant clipboard copy with visual toast confirmation.
- **Visual Feedback System:** Toast status banners indicating successful calculations, copy confirmations, or descriptive error warnings.

### Mathematical Operations
- **Core Arithmetic (Week 1):** Addition (`+`), Subtraction (`−`), Multiplication (`×`), and Division (`÷`).
- **Parentheses & Order of Operations:** Standard PEMDAS precedence support for complex expressions (e.g. `(15 + 5) × 3 = 60`).
- **Scientific & Helper Tools:**
  - Square Root (`√x`) with negative input guards.
  - Exponents / Power (`x²` and `xʸ` / `^`).
  - Reciprocal (`1/x`) with zero-division handling.
  - Percentage calculations (`%`).
  - Sign toggling (`±`).
- **Precision Cleaner:** Eliminates floating-point display noise (e.g., `0.1 + 0.2` cleanly displays `0.3` rather than `0.30000000000000004`).

### Strict Calculation Safety
- **No `eval()`:** Never uses unrestricted Python `eval()`. Instead, user expressions are evaluated node-by-node using Python's `ast` (Abstract Syntax Tree) module.
- **Graceful Error Recovery:** Division by zero returns `"Cannot divide by zero"` without crashing; syntax errors and invalid tokens return `"Invalid Expression"`.

### Desktop Keyboard Shortcuts
| Key / Shortcut | Action |
| :--- | :--- |
| `0` – `9` | Enter numbers |
| `+`, `-`, `*`, `/` | Arithmetic operators (`+`, `−`, `×`, `÷`) |
| `.` | Decimal point (guards against duplicate dots) |
| `(`, `)` | Parentheses |
| `%`, `^` | Percentage and Power |
| `Enter` / `=` | Calculate result |
| `BackSpace` | Delete last entered character |
| `Escape` / `C` / `c` | Clear All (`C`) |
| `Delete` | Clear Entry (`CE`) |
| `Ctrl + C` | Copy current result to clipboard |

---

## 3. Mapping of Week 1 Internship Requirements

| Requirement | Implementation File | Component / Function | Description |
| :--- | :--- | :--- | :--- |
| **Addition** | [`calculator.py`](file:///d:/Projects/Python%20Internship/Basic%20Calculator/calculator.py) | `add(a, b)` | Sums two numeric values. |
| **Subtraction** | [`calculator.py`](file:///d:/Projects/Python%20Internship/Basic%20Calculator/calculator.py) | `subtract(a, b)` | Subtracts second value from first. |
| **Multiplication** | [`calculator.py`](file:///d:/Projects/Python%20Internship/Basic%20Calculator/calculator.py) | `multiply(a, b)` | Multiplies two values. |
| **Division with Zero Check**| [`calculator.py`](file:///d:/Projects/Python%20Internship/Basic%20Calculator/calculator.py) | `divide(a, b)` | Divides values, safely returning `"Cannot divide by zero"`. |
| **Variables & Types** | [`calc_engine.py`](file:///d:/Projects/Python%20Internship/Basic%20Calculator/calc_engine.py) | `SafeExpressionEvaluator` | Validates numbers, strings, floats, and AST tokens. |
| **Conditional Logic** | [`calc_engine.py`](file:///d:/Projects/Python%20Internship/Basic%20Calculator/calc_engine.py) | `_eval_node()` | Directs operations strictly to whitelisted handlers. |
| **Exception Handling** | [`calc_engine.py`](file:///d:/Projects/Python%20Internship/Basic%20Calculator/calc_engine.py) | `try...except` | Catches `ZeroDivisionError`, `SyntaxError`, `ValueError`, and `OverflowError`. |
| **Original Terminal Menu** | [`calculator.py`](file:///d:/Projects/Python%20Internship/Basic%20Calculator/calculator.py) | `run_cli()` | Preserves the interactive while-loop terminal interface. |

---

## 4. Project Structure

```text
Basic Calculator/
├── main.py                     # Unified application entry point (Default: Launches GUI)
├── gui.py                      # Calculator Pro desktop Tkinter interface
├── calc_engine.py              # Safe AST math parser, scientific helpers, history tracker
├── calculator.py               # Original Week 1 basic arithmetic functions and CLI loop
├── calculator_original_backup.py # Immutable safety backup of original file
├── README.md                   # Complete documentation and user guide
└── tests/
    └── test_calculator.py     # 22 automated unit and integration tests
```

---

## 5. How to Run

### Method 1: Desktop Graphical Application (Default)
```powershell
python main.py
```
*(Or run `python gui.py` directly).*

### Method 2: Original Terminal Application
To run the interactive menu in the terminal:
```powershell
python main.py --cli
```
*(Or run `python calculator.py`).*

```text
===== BASIC CALCULATOR =====
1. Addition
2. Subtraction
3. Multiplication
4. Division
5. Exit
Choose an option (1-5):
```

### Method 3: Automated Test Suite
```powershell
python main.py --test
```
*(Or run `python -m unittest discover tests`).*

---

## 6. Example Calculations

| Input Expression | Evaluated Result | Notes |
| :--- | :--- | :--- |
| `12.5 + 7.5` | `20` | Clean decimal handling without trailing zeroes |
| `2 + 3 × 4` | `14` | Multiplications executed before addition (PEMDAS) |
| `(2 + 3) × 4` | `20` | Parentheses override standard operator precedence |
| `0.1 + 0.2` | `0.3` | Clean floating-point precision formatting |
| `250 × 15%` | `37.5` | Percentage of a number |
| `5 ^ 3` | `125` | Power / exponentiation calculation |
| `√(144)` | `12` | Square root utility |
| `1 / 4` | `0.25` | Reciprocal calculation |
| `100 ÷ 0` | `Cannot divide by zero` | Safe zero-division handling |

---

## 7. Automated Test Results

```text
test_floating_point_cleanup (test_calculator.TestFormattingAndHistory) ... ok
test_history_tracking (test_calculator.TestFormattingAndHistory) ... ok
test_gui_initialization_and_operations (test_calculator.TestGUI) ... ok
test_addition (test_calculator.TestOriginalOperations) ... ok
test_division (test_calculator.TestOriginalOperations) ... ok
test_division_by_zero (test_calculator.TestOriginalOperations) ... ok
test_multiplication (test_calculator.TestOriginalOperations) ... ok
test_subtraction (test_calculator.TestOriginalOperations) ... ok
test_basic_arithmetic (test_calculator.TestSafeExpressionEvaluator) ... ok
test_display_symbols (test_calculator.TestSafeExpressionEvaluator) ... ok
test_division_by_zero_handling (test_calculator.TestSafeExpressionEvaluator) ... ok
test_invalid_expressions (test_calculator.TestSafeExpressionEvaluator) ... ok
test_operator_precedence_pemdas (test_calculator.TestSafeExpressionEvaluator) ... ok
test_parentheses (test_calculator.TestSafeExpressionEvaluator) ... ok
test_percentages (test_calculator.TestSafeExpressionEvaluator) ... ok
test_powers (test_calculator.TestSafeExpressionEvaluator) ... ok
test_security_rejection_of_arbitrary_code (test_calculator.TestSafeExpressionEvaluator) ... ok
test_unary_minus (test_calculator.TestSafeExpressionEvaluator) ... ok
test_percentage (test_calculator.TestScientificHelpers) ... ok
test_reciprocal (test_calculator.TestScientificHelpers) ... ok
test_square (test_calculator.TestScientificHelpers) ... ok
test_square_root (test_calculator.TestScientificHelpers) ... ok

----------------------------------------------------------------------
Ran 22 tests in 1.503s

OK
```

All 22 unit and integration tests passed (100% success rate).

---

## 8. Safety & Isolation Notice
- **Week 2** ([`Student Management System`](file:///d:/Projects/Python%20Internship/Student%20Management%20System)), **Week 3** ([`Weather App`](file:///d:/Projects/Python%20Internship/Weather%20App)), and **Week 4** ([`QuizUp Python Edition`](file:///d:/Projects/Python%20Internship/QuizUp%20Python%20Edition)) remain completely untouched.
- All changes are stored locally; nothing has been pushed to GitHub.
