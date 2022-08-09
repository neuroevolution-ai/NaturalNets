"""Contains all enums used by different components of the app."""

from enum import Enum

class FontStyle(Enum):
    """Represents a font-style. The value is a string description of the font-style."""
    BOLD = "Bold"
    ITALIC = "Italic"
    UNDERLINE = "Underline"

class Font(Enum):
    """Represents a font. The value is a string description of the font."""
    DEJAVU_SANS = "DejaVu Sans"
    LIBERATION_MONO = "Liberation Mono"
    NIMBUS_ROMAN = "Nimbus Roman"
    UBUNTU = "Ubuntu"

class Car(Enum):
    """Represents a car. The value is an integer."""
    A = 1
    B = 2
    C = 3

class Color(Enum):
    """Represents a color. The value is a (R,G,B) tuple."""
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    BROWN = (64, 37, 16)

class Base(Enum):
    """Represents a numeral base for the calculator."""
    DECIMAL = 0
    BINARY = 2
    HEX = 16

class Operator(Enum):
    """Represents a mathematical operator for the calculator."""
    ADDITION = "+"
    SUBTRACTION = "-"
    MULTIPLICATION = "*"
    DIVISION = "/"

class Figure(Enum):
    """Represents a figure in the figure-printer. The value is the file-name of that figure."""
    CHRISTMAS_TREE = "figure_christmas_tree.png"
    SPACE_SHIP = "figure_space_ship.png"
    GUITAR = "figure_guitar.png"
    HOUSE = "figure_house.png"
