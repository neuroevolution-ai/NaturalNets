
from typing import Callable, List
import cv2

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.exception import ArgumentError
from naturalnets.environments.gui_app.page import Widget
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton


class Textfield(Widget):

    STATE_LEN = 1

    def __init__(self, bounding_box: BoundingBox, click_action: Callable = None):
        super().__init__(self.STATE_LEN, bounding_box)
        self._bounding_box = bounding_box
        self._click_action = click_action

    def handle_click(self, click_position: np.ndarray = None) -> None:
        """ Executes this RadioButtons action, if any.

        Args:
            click_position (np.ndarray, optional): Not used. Defaults to None.
        """
        if self.has_click_action():
            self._click_action()

        # this implementation of a textfield works like a radio button click it once and the text field is selected and the text is rendered
        # click it again and the text is no longer rendered
        self.enter_value()

    def has_click_action(self):
        return self._click_action is not None

    def set_selected(self, selected: int):
        self.get_state()[0] = selected

    def is_selected(self) -> int:
        return self.get_state()[0]

    def enter_value(self):
        if (self.is_selected()):
            self.set_selected(False)
        else:
            self.set_selected(True)

    def render(self, img: np.ndarray) -> np.ndarray:

        if self.is_selected():
            width = self._bounding_box.width
            height = int(self._bounding_box.height/2)
            
            int  # width, height of the square part of the checkbox
            thickness = 2
            cross_color = (0, 0, 0)
            text = "Sample Text for Textfield"
            font = cv2.FONT_HERSHEY_SIMPLEX

            x, y = self.get_bb().get_as_tuple()[0:2]
            # Modify x, y, width, height s.t. the cross does not surpass the box-limits
            cv2.putText(img, text, (x, y+height), font, 1, color=(0, 0, 0), thickness=2)
            #cv2.line(img, (x, y), (x + width, y + height), cross_color, thickness, lineType=cv2.LINE_AA)
            #v2.line(img, (x + width, y), (x, y + height), cross_color, thickness, lineType=cv2.LINE_AA)

        return img

    def reset(self):
        self.set_selected(False)
