"""This module contains the PasswordCard class, which is a widget that can be clicked on to show a password card."""
from typing import Callable

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Widget
from naturalnets.environments.gui_app.widgets.button import Button


class PasswordCard(Widget, Button):
    '''
    Represents a PasswordCard that can be clicked on to show a password card.

    State:
        0: not showing_passwordcard
        1: showing_passwordcard
    '''

    STATE_LEN = 1

    def __init__(self, bounding_box: BoundingBox, click_action: Callable = None):
        Widget.__init__(self, self.STATE_LEN, bounding_box)
        Button.__init__(self, bounding_box, click_action)
        self.showing_passwordcard = False

    def show_or_hide_passwordcard(self):
        '''
        Toggles the showing_password attribute of the button.
        '''
        self.showing_passwordcard = not self.showing_passwordcard

    def handle_click(self, click_position: np.ndarray) -> None:

        if self._click_action:
            self._click_action()
        self.show_or_hide_passwordcard()

    def render(self, img: np.ndarray) -> np.ndarray:
        return img

    def has_click_action(self) -> bool:
        '''
        Returns True if the button has a click-action.
        '''
        return self._click_action is not None

    def is_selected(self) -> bool:
        '''
        Returns True if the button is selected.
        '''
        return self.showing_passwordcard

    def set_selected(self, selected: bool):
        '''
        Sets the selected attribute of the button.
        '''
        self.showing_passwordcard = selected

    def reset(self):
        '''
        Resets the button.
        '''
        self.showing_passwordcard = False
