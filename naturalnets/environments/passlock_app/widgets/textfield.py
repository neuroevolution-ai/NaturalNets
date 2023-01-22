
from typing import Callable, List

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
        if (self.is_selected()):
            self.set_selected(False)
        else:
            self.set_selected(True)

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
        return super().render(img)

    def reset(self):
        self.set_selected(False)
