from enum import Enum


class Color(Enum):
    """Represents a color. The value is a (R,G,B) tuple."""

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    BROWN = (64, 37, 16)
    ORANGE = (0, 88, 255)
