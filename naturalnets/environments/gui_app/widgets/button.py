import os
from typing import Callable
import cv2

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.page import Widget
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.passlock_app.widgets.textfield import Textfield


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


class ToggleButton(Widget, Button):
    '''
    Represents a ToggleButton that can be clicked on to toggle between two states.
    On click a picture is rendered onto the button. The can be set with the set_img_path method.
    '''

    STATE_LEN = 1
    IMG_PATH = None

    def __init__(self, bounding_box: BoundingBox, click_action: Callable = None):
        Widget.__init__(self, self.STATE_LEN, bounding_box)
        Button.__init__(self, bounding_box, click_action)
        self.toggle_on = False

    def toggle(self):
        '''
        Toggles the state of the button.
        '''
        self.toggle_on = not self.toggle_on

    def handle_click(self, click_position: np.ndarray):
        '''
        Handles a click on the button. If the button has a click action, it is executed.
        '''

        if self.has_click_action():
            self._click_action()
        self.toggle()

    def render(self, img: np.ndarray) -> np.ndarray:
        '''
        Renders the button onto the given image.
        args:
            img: the image to render the button onto.
        returns:
            the rendered image.
        '''
        if self.IMG_PATH is not None:
            if self.is_selected():
                to_render = cv2.imread(self.IMG_PATH)
                to_render = cv2.resize(
                    to_render, (self._bounding_box.width, self._bounding_box.height))
                img = render_onto_bb(img, self._bounding_box, to_render)

        return img

    def has_click_action(self) -> bool:
        '''
        Returns True if the button has a click action.
        '''
        return self._click_action is not None

    def is_selected(self) -> bool:
        '''
        Returns True if the button is selected.
        '''
        return self.toggle_on

    def set_selected(self, selected: bool):
        '''
        Sets the selected state of the button.
        '''
        self.toggle_on = selected

    def reset(self):
        '''
        Resets the button to its initial state.
        '''
        self.set_selected(False)

    def set_img_path(self, path):
        '''
        Sets the path of the image to be rendered.
        '''
        self.IMG_PATH = path


class ShowPasswordButton(ToggleButton):
    '''
    Represents a ShowPasswordButton that can be clicked on to show a password.
    '''

    def __init__(self, bounding_box: BoundingBox, click_action: Callable = None, color: tuple = (0, 0, 0)):
        ToggleButton.__init__(self, bounding_box, click_action)
        self.color = color
        self.IMG_PATH = os.path.join(
            "naturalnets", "environments", "passlock_app", "img", "password_shown_button.PNG")

    def show_password_of_textfield(self, textfield: Textfield):
        '''
        Shows the password of the given textfield.
        '''
        if not self.is_selected():
            textfield.set_text("Password Shown")
        else:
            textfield.set_text("Sample Text for Textfield")
