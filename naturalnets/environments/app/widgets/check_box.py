import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.page import Widget

class CheckBox(Widget):

    STATE_LEN = 1

    def __init__(self, bounding_box:BoundingBox):
        super().__init__(self.STATE_LEN, bounding_box)

    def handle_click(self):
        if self.get_state()[0] == 0:
            self.get_state()[0] = 1
        else:
            self.get_state()[0] = 0

    def is_checked(self):
        return self.get_state()[0]

    def render(self, img:np.ndarray) -> np.ndarray:
        if self.is_checked():
            cross_color = (0,0,0)
            thickness = 2
            x, y, width, height = self.get_bb().get_as_tuple()
            x += 2
            y += 2
            width -= 4
            height -= 4
            cv2.line(img, (x, y), (x + width, y + height), cross_color, thickness)
            cv2.line(img, (x + width, y), (x, y + height), cross_color, thickness)
        return img