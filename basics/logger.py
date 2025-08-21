"""
logger.py

Provides utility functions for logging with colored text output in the terminal. 

Functions:
    - color_text: Formats text with ANSI color codes for terminal display.
"""

def color_text(text, color):
    """
    Formats the given text with the specified color using ANSI escape codes.

    Parameters:
        text (str): The text to be formatted.
        color (str): The name of the color. Supported colors are:
                     - 'red'
                     - 'green'
                     - 'yellow'
                     - 'blue'
                     - 'purple'
                     - 'cyan'
                     - 'white'
                     - 'orange'
                     - 'reset' (resets formatting to default)

    Returns:
        str: The formatted text with the specified color.

    Raises:
        KeyError: If the provided color is not in the predefined color list.

    Example:
        >>> print(color_text("Error!", "red"))
        (Displays "Error!" in red text in the terminal)
    """
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'orange': '\033[38;5;208m',
        'reset': '\033[0m'
    }
    
    # Raise an error if an invalid color is provided
    if color not in colors:
        raise KeyError(f"Invalid color '{color}'. Supported colors: {', '.join(colors.keys())}")

    # Return formatted text with the specified color
    return colors[color] + text + colors['reset']