"""Calculator Pro — Main Unified Application Entry Point.
======================================================
Launches Calculator Pro Desktop GUI by default, while maintaining
seamless access to the original Week 1 terminal menu and automated tests.

Usage:
    python main.py            # Launch Calculator Pro Desktop GUI (Default)
    python main.py --cli      # Launch original Week 1 terminal interactive menu
    python main.py --test     # Run automated test suite
"""

import os
import sys

# Ensure local directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main routing entry point."""
    args = sys.argv[1:]

    if "--cli" in args or "-c" in args:
        import calculator
        calculator.run_cli()
    elif "--test" in args or "-t" in args:
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    elif "--help" in args or "-h" in args:
        print(__doc__)
    else:
        # Default: Launch desktop GUI
        from gui import launch_gui
        launch_gui()


if __name__ == "__main__":
    main()
