from typing import Callable
import cv2

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.page import Widget


class Button(Clickable):
    """Represents a Button with a click-action.
    """

    def __init__(self, bounding_box: BoundingBox, click_action: Callable):
        self._bounding_box = bounding_box
        self._click_action = click_action

    def get_bb(self):
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def handle_click(self, click_position: np.ndarray) -> None:
        self._click_action()

class ShowPasswordButton(Widget, Button):

    STATE_LEN = 1

    def __init__(self, bounding_box: BoundingBox, click_action: Callable = None):
        Widget.__init__(self, self.STATE_LEN, bounding_box)
        Button.__init__(self, bounding_box, click_action)
        self.showing_password = False
    
    def show_or_hide_password(self):
        if self.showing_password:
            self.showing_password = False
        else:
            self.showing_password = True

    def handle_click(self, click_position: np.ndarray) -> None:

        if(self._click_action):
            self._click_action()
        self.show_or_hide_password()

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box
    
    def render(self, img: np.ndarray) -> np.ndarray:
        if self.is_selected():
            width = height = self._bounding_box.height  # width, height of the square part of the checkbox
            thickness = 2
            color = (96, 134, 247)

            x, y = self.get_bb().get_as_tuple()[0:2]
            # Modify x, y, width, height s.t. the cross does not surpass the box-limits
            x += 2
            y += 2
            width -= 4
            height -= 4

            cv2.line(img, (x, y), (x + width, y + height), color, thickness, lineType=cv2.LINE_AA)
            cv2.line(img, (x + width, y), (x, y + height), color, thickness, lineType=cv2.LINE_AA)
        return img

    def has_click_action(self) -> bool:
        if self._click_action is not None:
            return True
    
    def is_selected(self) -> bool:
        return self.showing_password