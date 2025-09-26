"""
Test functions for the persistent kernel
"""

def greet(name):
    """Simple greeting function."""
    return f"Hello, {name}!"

def multiply(x, y):
    """Multiply two numbers."""
    return x * y

def format_message(msg, name):
    """Format a message with a name."""
    return f"{msg}, {name}! How are you today?"

# Functions dictionary for easy access
FUNCTIONS = {
    "greet": greet,
    "multiply": multiply,
    "format_message": format_message
}

__all__ = ["greet", "multiply", "format_message", "FUNCTIONS"]
