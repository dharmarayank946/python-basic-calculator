"""Calculator Pro — Safe Calculation Engine.
=========================================
Implements safe mathematical expression evaluation without `eval()`.
Uses Python's `ast` (Abstract Syntax Tree) module to restrict operations
strictly to numbers and verified arithmetic operators.

Features:
- Preserves and utilizes Week 1 core arithmetic (`add`, `subtract`, `multiply`, `divide`).
- Extended operations: power (`^`), percentage (`%`), square root (`√`), reciprocal (`1/x`).
- AST recursive evaluator prohibiting arbitrary code execution, functions, and imports.
- Graceful division-by-zero and malformed expression error handling.
- Clean number formatting eliminating floating-point display noise (e.g. 0.1 + 0.2 -> 0.3).
- In-memory calculation history tracking.
"""

import ast
import math
from datetime import datetime
from typing import Union, List, Dict, Any

# Import original Week 1 functions
from calculator import add, subtract, multiply, divide


class SafeExpressionEvaluator:
    """Safe mathematical evaluator using AST parsing without unrestricted eval()."""

    # Whitelist of permissible binary operators
    ALLOWED_OPERATORS = {
        ast.Add: add,
        ast.Sub: subtract,
        ast.Mult: multiply,
        ast.Div: divide,
        ast.Mod: lambda a, b: a % b if b != 0 else "Cannot divide by zero",
        ast.Pow: lambda a, b: math.pow(a, b),
    }

    # Whitelist of permissible unary operators
    ALLOWED_UNARY = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
    }

    @classmethod
    def evaluate(cls, expression: str) -> Union[int, float, str]:
        """Safely parse and evaluate a mathematical expression string."""
        clean_expr = cls._sanitize_expression(expression)
        if not clean_expr:
            return 0

        try:
            tree = ast.parse(clean_expr, mode="eval")
            result = cls._eval_node(tree.body)

            # Check if error string was propagated from divide
            if isinstance(result, str):
                return result

            # Check for NaN / Infinity
            if math.isnan(result):
                return "Undefined"
            if math.isinf(result):
                return "Overflow"

            return result
        except ZeroDivisionError:
            return "Cannot divide by zero"
        except (SyntaxError, ValueError, TypeError, OverflowError):
            return "Invalid Expression"

    @classmethod
    def _sanitize_expression(cls, expr: str) -> str:
        """Convert visual math symbols and percentages into valid Python AST tokens."""
        s = expr.strip()
        # Replace visual symbols
        s = s.replace("×", "*").replace("÷", "/")
        s = s.replace("−", "-").replace("—", "-")
        s = s.replace("^", "**")

        # Handle percentage: replace number followed by % with (/100)
        # e.g. "50%" -> "(50/100)"
        import re
        s = re.sub(r'(\d+(?:\.\d+)?)%', r'(\1/100)', s)

        return s

    @classmethod
    def _eval_node(cls, node: ast.AST) -> Union[int, float, str]:
        """Recursively evaluate an AST node strictly against the whitelist."""
        # Numeric literal
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        # Python < 3.8 backwards compatibility
        if isinstance(node, getattr(ast, "Num", ())) :
            return node.n

        # Binary operation: a + b, a * b, a / b, etc.
        if isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left)
            if isinstance(left, str):
                return left

            right = cls._eval_node(node.right)
            if isinstance(right, str):
                return right

            op_type = type(node.op)
            if op_type in cls.ALLOWED_OPERATORS:
                handler = cls.ALLOWED_OPERATORS[op_type]
                try:
                    res = handler(left, right)
                    return res
                except ZeroDivisionError:
                    return "Cannot divide by zero"
                except OverflowError:
                    return "Overflow"
            raise ValueError(f"Operator {op_type} is not permitted.")

        # Unary operation: -x, +x
        if isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand)
            if isinstance(operand, str):
                return operand

            op_type = type(node.op)
            if op_type in cls.ALLOWED_UNARY:
                handler = cls.ALLOWED_UNARY[op_type]
                return handler(operand)
            raise ValueError(f"Unary operator {op_type} is not permitted.")

        # Disallow any other syntax (Function calls, Variables, Imports, Attributes)
        raise ValueError(f"Disallowed AST expression construct: {type(node).__name__}")


def safe_square_root(value: float) -> Union[float, str]:
    """Calculate square root with domain validation."""
    try:
        val = float(value)
        if val < 0:
            return "Negative square root"
        return math.sqrt(val)
    except (ValueError, TypeError):
        return "Invalid Input"


def safe_reciprocal(value: float) -> Union[float, str]:
    """Calculate reciprocal (1 / x) using original divide function."""
    try:
        val = float(value)
        return divide(1.0, val)
    except (ValueError, TypeError):
        return "Invalid Input"


def safe_percentage(value: float) -> Union[float, str]:
    """Calculate percentage (value / 100)."""
    try:
        val = float(value)
        return divide(val, 100.0)
    except (ValueError, TypeError):
        return "Invalid Input"


def safe_square(value: float) -> Union[float, str]:
    """Calculate power of 2 (x^2)."""
    try:
        val = float(value)
        return multiply(val, val)
    except (ValueError, TypeError):
        return "Invalid Input"


def format_display_number(value: Union[int, float, str]) -> str:
    """Format numeric outputs cleanly, eliminating floating point noise.
    
    Examples:
    - 0.1 + 0.2 -> 0.3 (not 0.30000000000000004)
    - 5.0 -> 5
    - 1250000000000.0 -> scientific notation
    """
    if isinstance(value, str):
        return value

    if isinstance(value, (int, float)):
        # Check if integer equivalent
        if isinstance(value, float) and value.is_integer():
            return str(int(value))

        # Round to 10 decimal places to eliminate IEEE 754 precision noise
        rounded = round(value, 10)
        if rounded.is_integer():
            return str(int(rounded))

        # Format float and strip trailing zeroes
        formatted = f"{rounded:.10f}".rstrip("0").rstrip(".")

        # Guard against scientific notation display if number is extremely large or tiny
        if len(formatted) > 16:
            formatted = f"{value:.8e}"

        return formatted

    return str(value)


class CalculationHistory:
    """Manages an in-memory calculation session history."""

    def __init__(self, max_items: int = 50):
        self.max_items = max_items
        self._history: List[Dict[str, Any]] = []

    def add_entry(self, expression: str, result: str):
        """Append a calculation entry."""
        if not expression or not result:
            return
        entry = {
            "expression": expression,
            "result": result,
            "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        }
        self._history.insert(0, entry)
        if len(self._history) > self.max_items:
            self._history.pop()

    def get_entries(self) -> List[Dict[str, Any]]:
        """Return the list of history entries."""
        return list(self._history)

    def clear(self):
        """Clear all history entries."""
        self._history.clear()
