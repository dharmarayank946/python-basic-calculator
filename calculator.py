"""Week 1 Basic Calculator — Original Arithmetic Core.

Contains the foundational Week 1 arithmetic functions:
- add(a, b)
- subtract(a, b)
- multiply(a, b)
- divide(a, b)
Preserves the original interactive terminal menu interface.
"""


# Function to perform addition
def add(a, b):
    return a + b


# Function to perform subtraction
def subtract(a, b):
    return a - b


# Function to perform multiplication
def multiply(a, b):
    return a * b


# Function to perform division with zero check
def divide(a, b):
    if b == 0:
        return "Cannot divide by zero"
    return a / b


def run_cli():
    """Display the calculator menu and handle terminal interactions."""
    while True:
        print("\n===== BASIC CALCULATOR =====")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Exit")

        # Get the user's choice
        choice = input("Choose an option (1-5): ")

        # Exit the calculator
        if choice == "5":
            print("Thank you for using the calculator!")
            break

        # Validate the menu choice
        if choice not in ("1", "2", "3", "4"):
            print("Invalid choice. Please try again.")
            continue

        # Get numbers and handle invalid numeric input
        try:
            num1 = float(input("Enter the first number: "))
            num2 = float(input("Enter the second number: "))
        except ValueError:
            print("Please enter valid numbers.")
            continue

        # Perform the selected arithmetic operation
        if choice == "1":
            result = add(num1, num2)
        elif choice == "2":
            result = subtract(num1, num2)
        elif choice == "3":
            result = multiply(num1, num2)
        else:
            result = divide(num1, num2)

        # Display the result
        print("Result:", result)


if __name__ == "__main__":
    run_cli()
