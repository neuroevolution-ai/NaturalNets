from typing import Callable

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
        return super().render(img)

    def has_click_action(self) -> bool:
        if self._click_action is not None:
            return True
    
    def is_password_shown(self) -> bool:
        return self.showing_password