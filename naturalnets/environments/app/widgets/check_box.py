"""Module containing the CheckBox class.
"""
from typing import Callable

import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.enums import Color
from naturalnets.environments.app.page import Widget


class CheckBox(Widget):
    """Widget representing a checkbox.

       State description:
            state[0]: the selected-state of this checkbox.
    """

    STATE_LEN = 1

    def __init__(self, bounding_box: BoundingBox, action: Callable = None):
        """
        Args:
            bounding_box (BoundingBox): The BoundingBox of this checkbox.
            action (Callable, optional): An action to be executed on-click. Defaults to None.
        """
        super().__init__(self.STATE_LEN, bounding_box)
        self.action = action

    def handle_click(self, click_position: np.ndarray):
        """Toggles the selected state of this checkbox and executes its action, if any.
        """
        if self.get_state()[0] == 0:
            self.get_state()[0] = 1
        else:
            self.get_state()[0] = 0

        if self.action is not None:
            self.action(self.get_state()[0])

    def is_selected(self) -> int:
        return self.get_state()[0]

    def set_selected(self, selected: int):
        self.get_state()[0] = selected
        if self.action is not None:
            self.action(self.get_state()[0])

    def render(self, img: np.ndarray) -> np.ndarray:
        if self.is_selected():
            width = height = 14  # width, height of the square part of the checkbox
            thickness = 2
            cross_color = Color.BLACK.value

            x, y = self.get_bb().get_as_tuple()[0:2]
            # Modify x, y, width, height s.t. the cross does not surpass the box-limits
            x += 2
            y += 2
            width -= 4
            height -= 4

            cv2.line(img, (x, y), (x + width, y + height), cross_color, thickness)
            cv2.line(img, (x + width, y), (x, y + height), cross_color, thickness)
        return img
