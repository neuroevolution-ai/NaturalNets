import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.colors import Color
from naturalnets.environments.app.page import Widget

class CheckBox(Widget):

    STATE_LEN = 1

    def __init__(self, bounding_box:BoundingBox):
        super().__init__(self.STATE_LEN, bounding_box)

    def handle_click(self, click_position: np.ndarray = None):
        if self.get_state()[0] == 0:
            self.get_state()[0] = 1
        else:
            self.get_state()[0] = 0

    def is_selected(self):
        return self.get_state()[0]

    def set_selected(self, selected:int) -> None:
        self.get_state()[0] = selected
        
    def render(self, img:np.ndarray) -> np.ndarray:
        width = height = 14 # width,height of the square part of the checkbox
        if self.is_selected():
            cross_color = Color.BLACK.value
            thickness = 2
            x, y = self.get_bb().get_as_tuple()[0:2]
            x += 2
            y += 2
            width -= 4
            height -= 4
            cv2.line(img, (x, y), (x + width, y + height), cross_color, thickness)
            cv2.line(img, (x + width, y), (x, y + height), cross_color, thickness)
        return img