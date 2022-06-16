import numpy as np

class ElementBB():
    """ Describes the bounding-box of an element in pixels.
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

    def __repr__(self):
        return "({0},{1},{2},{3})".format(self.x,self.y,self.width,self.height)
