
from typing import Callable
import cv2

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Widget


class Slider(Widget):

    STATE_LEN = 0

    def __init__(self, bounding_box: BoundingBox, states, action: Callable = None):
        """
        Args:

        """
        self.STATE_LEN = states
        self.action = action
        super().__init__(self.STATE_LEN, bounding_box)

    def render(self, img: np.ndarray) -> np.ndarray:

        thickness = 2
        color = (0, 0, 0)
        radius = 16
        
        width = self._bounding_box.width-2*radius # width, height of the square part of the checkbox
        height = int(self._bounding_box.height/2)  # width, height of the square part of the checkbox
        
        x, y = self.get_bb().get_as_tuple()[0:2]
        # Modify x, y, width, height s.t. the cross does not surpass the box-limits
        x += radius
        if(self._state[2]): postion = (x +(int(width/2)*2), y+height)
        if(self._state[1]): postion = (x +(int(width/2)*1), y+height)
        if(self._state[0]): postion = (x, y+height)

        cv2.circle(img, postion, radius, color, thickness, lineType=cv2.LINE_AA)
        return img

    def handle_click(self, click_position: np.ndarray = None) -> None:
        if (self.has_click_action()):
            self.action()

        self._state = np.roll(self.get_state(), 1)

    def has_click_action(self):
        if self.action is not None:
            return True

    def set_slider_value(self, state):
        self.get_state()[state] = 1

    def get_slider_value(self):
        return np.argmax(self.get_state())
