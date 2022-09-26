import numpy as np


class BoundingBox:
    """ Describes the bounding-box consisting of the x, y, width, and height of an element in pixels.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # generate values needed to check if a point is inside this bounding box
        self.x1 = self.x
        self.x2 = self.x1 + self.width
        self.y1 = self.y
        self.y2 = self.y1 + self.height

    def is_point_inside(self, point: np.ndarray):
        """Returns true if the given x and y are inside the bounding box (including its borders).
        """
        x = point[0]
        y = point[1]

        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def get_as_tuple(self):
        """Returns the BoundingBox values as a Tuple (x, y, width, height)."""
        return self.x, self.y, self.width, self.height

    def __repr__(self):
        return f"({self.x},{self.y},{self.width},{self.height})"
