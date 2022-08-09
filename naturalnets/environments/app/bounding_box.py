"""Contains the BoundingBox class."""
import numpy as np

class BoundingBox():
    """ Describes the bounding-box consisting of the x, y, width, and height of an element in pixels.
    """
    def __init__(self, x:int, y:int, width:int, height:int):
        self.x = x
        self.y = y
        self.width = width
        self.height= height

    def is_point_inside(self, point:np.ndarray):
        """Returns true if the given x and y are inside the bounding box (including its borders).
        """
        x = point[0]
        y = point[1]

        x1 = self.x
        x2 = x1 + self.width
        y1 = self.y
        y2 = y1 + self.height
        return x1 <= x <= x2 and y1 <= y <= y2

    def get_as_tuple(self):
        """Returns the BoundingBox values as a Tuple (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)

    def __repr__(self):
        return f"({self.x},{self.y},{self.width},{self.height})"
