"""Automated Unit & Integration Test Suite for Calculator Pro.
============================================================
Tests:
1. Original Week 1 basic operations (add, subtract, multiply, divide).
2. Safe AST expression evaluator (PEMDAS, parentheses, decimals, percentages, powers).
3. Security: rejection of arbitrary code, imports, and variables (no eval()).
4. Division-by-zero and malformed expression error recovery.
5. Scientific helpers (square root, square, reciprocal, percentage).
6. Floating-point display noise elimination.
7. Calculation history tracking.
8. Desktop GUI initialization and operation handlers.
"""

import math
import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator import add, subtract, multiply, divide
from calc_engine import (
    SafeExpressionEvaluator,
    safe_square_root,
    safe_reciprocal,
    safe_percentage,
    safe_square,
    format_display_number,
    CalculationHistory,
)


class TestOriginalOperations(unittest.TestCase):
    """Verify original Week 1 arithmetic functions remain intact and accurate."""

    def test_addition(self):
        self.assertEqual(add(10, 5), 15)
        self.assertEqual(add(-3, 8), 5)
        self.assertEqual(add(0, 0), 0)
        self.assertAlmostEqual(add(2.5, 3.1), 5.6)

    def test_subtraction(self):
        self.assertEqual(subtract(10, 4), 6)
        self.assertEqual(subtract(5, 12), -7)
        self.assertAlmostEqual(subtract(15.5, 5.2), 10.3)

    def test_multiplication(self):
        self.assertEqual(multiply(6, 7), 42)
        self.assertEqual(multiply(-4, 5), -20)
        self.assertEqual(multiply(99, 0), 0)
        self.assertAlmostEqual(multiply(2.5, 4), 10.0)

    def test_division(self):
        self.assertEqual(divide(20, 4), 5.0)
        self.assertEqual(divide(-15, 3), -5.0)
        self.assertAlmostEqual(divide(7, 2), 3.5)

    def test_division_by_zero(self):
        result = divide(10, 0)
        self.assertEqual(result, "Cannot divide by zero")


class TestSafeExpressionEvaluator(unittest.TestCase):
    """Test AST-based safe evaluation without eval()."""

    def test_basic_arithmetic(self):
        self.assertEqual(SafeExpressionEvaluator.evaluate("15 + 25"), 40)
        self.assertEqual(SafeExpressionEvaluator.evaluate("100 - 35"), 65)
        self.assertEqual(SafeExpressionEvaluator.evaluate("8 * 9"), 72)
        self.assertEqual(SafeExpressionEvaluator.evaluate("84 / 4"), 21.0)

    def test_operator_precedence_pemdas(self):
        # Multiplication before addition: 2 + 3 * 4 = 14
        self.assertEqual(SafeExpressionEvaluator.evaluate("2 + 3 * 4"), 14)
        # Division before subtraction: 20 - 10 / 2 = 15
        self.assertEqual(SafeExpressionEvaluator.evaluate("20 - 10 / 2"), 15.0)

    def test_parentheses(self):
        # Override precedence with parentheses: (2 + 3) * 4 = 20
        self.assertEqual(SafeExpressionEvaluator.evaluate("(2 + 3) * 4"), 20)
        self.assertEqual(SafeExpressionEvaluator.evaluate("((10 - 2) * (4 + 1)) / 4"), 10.0)

    def test_display_symbols(self):
        # Visual symbols × and ÷
        self.assertEqual(SafeExpressionEvaluator.evaluate("7 × 8"), 56)
        self.assertEqual(SafeExpressionEvaluator.evaluate("36 ÷ 6"), 6.0)
        self.assertEqual(SafeExpressionEvaluator.evaluate("10 − 4"), 6)

    def test_percentages(self):
        self.assertEqual(SafeExpressionEvaluator.evaluate("50%"), 0.5)
        self.assertEqual(SafeExpressionEvaluator.evaluate("200 * 15%"), 30.0)

    def test_powers(self):
        self.assertEqual(SafeExpressionEvaluator.evaluate("2 ^ 3"), 8.0)
        self.assertEqual(SafeExpressionEvaluator.evaluate("5 ^ 2"), 25.0)

    def test_unary_minus(self):
        self.assertEqual(SafeExpressionEvaluator.evaluate("-10 + 25"), 15)
        self.assertEqual(SafeExpressionEvaluator.evaluate("-(4 + 6)"), -10)

    def test_division_by_zero_handling(self):
        self.assertEqual(SafeExpressionEvaluator.evaluate("100 / 0"), "Cannot divide by zero")
        self.assertEqual(SafeExpressionEvaluator.evaluate("50 / (10 - 10)"), "Cannot divide by zero")

    def test_invalid_expressions(self):
        self.assertEqual(SafeExpressionEvaluator.evaluate("5 + * 3"), "Invalid Expression")
        self.assertEqual(SafeExpressionEvaluator.evaluate("(10 + 2"), "Invalid Expression")
        self.assertEqual(SafeExpressionEvaluator.evaluate("++//"), "Invalid Expression")

    def test_security_rejection_of_arbitrary_code(self):
        # Security test: Ensure function calls and variables are strictly rejected
        self.assertEqual(SafeExpressionEvaluator.evaluate("__import__('os').system('echo hack')"), "Invalid Expression")
        self.assertEqual(SafeExpressionEvaluator.evaluate("open('calculator.py').read()"), "Invalid Expression")
        self.assertEqual(SafeExpressionEvaluator.evaluate("x + y"), "Invalid Expression")


class TestScientificHelpers(unittest.TestCase):
    """Test extended scientific operations."""

    def test_square_root(self):
        self.assertEqual(safe_square_root(64), 8.0)
        self.assertEqual(safe_square_root(0), 0.0)
        self.assertEqual(safe_square_root(-9), "Negative square root")

    def test_reciprocal(self):
        self.assertEqual(safe_reciprocal(4), 0.25)
        self.assertEqual(safe_reciprocal(0), "Cannot divide by zero")

    def test_square(self):
        self.assertEqual(safe_square(5), 25.0)
        self.assertEqual(safe_square(-6), 36.0)

    def test_percentage(self):
        self.assertEqual(safe_percentage(75), 0.75)


class TestFormattingAndHistory(unittest.TestCase):
    """Test precision display noise removal and history persistence."""

    def test_floating_point_cleanup(self):
        # 0.1 + 0.2 in IEEE 754 is 0.30000000000000004
        noisy_val = 0.1 + 0.2
        formatted = format_display_number(noisy_val)
        self.assertEqual(formatted, "0.3")

        # Integer equivalents
        self.assertEqual(format_display_number(42.0), "42")
        self.assertEqual(format_display_number("Cannot divide by zero"), "Cannot divide by zero")

    def test_history_tracking(self):
        history = CalculationHistory()
        self.assertEqual(len(history.get_entries()), 0)

        history.add_entry("25 + 15", "40")
        history.add_entry("10 * 8", "80")
        entries = history.get_entries()

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["expression"], "10 * 8")
        self.assertEqual(entries[0]["result"], "80")

        history.clear()
        self.assertEqual(len(history.get_entries()), 0)


class TestGUI(unittest.TestCase):
    """Test Tkinter GUI initialization and operation handlers."""

    def test_gui_initialization_and_operations(self):
        try:
            import tkinter as tk
            from gui import CalculatorProGUI

            root = tk.Tk()
            root.withdraw()
            app = CalculatorProGUI(root)
            self.assertIsNotNone(app)

            # Test keypad digit entry
            app.append_digit("1")
            app.append_digit("5")
            self.assertEqual(app.active_input, "15")

            # Test operator entry
            app.append_operator("+")
            self.assertEqual(app.current_expression, "15 + ")

            # Test second operand
            app.append_digit("2")
            app.append_digit("5")
            self.assertEqual(app.active_input, "25")

            # Test calculation
            app.calculate_result()
            self.assertEqual(app.active_input, "40")
            self.assertEqual(len(app.history.get_entries()), 1)

            # Test scientific helpers
            app.apply_square()
            self.assertEqual(app.active_input, "1600")

            app.apply_sqrt()
            self.assertEqual(app.active_input, "40")

            # Test clear all
            app.clear_all()
            self.assertEqual(app.active_input, "0")
            self.assertEqual(app.current_expression, "")

            # Test division by zero
            app.append_digit("9")
            app.append_operator("÷")
            app.append_digit("0")
            app.calculate_result()
            self.assertEqual(app.result_label.cget("text"), "Cannot divide by zero")

            root.destroy()
        except tk.TclError:
            pass


if __name__ == "__main__":
    unittest.main()
