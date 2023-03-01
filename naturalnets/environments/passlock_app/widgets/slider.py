'''A slider widget. Clicking on it will change its state and execute the given action.'''
from typing import Callable
import cv2

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Widget


class Slider(Widget):
    '''
    A slider widget. Clicking on it will change its state and execute the given action.
    '''

    STATE_LEN = 1

    def __init__(self, bounding_box: BoundingBox, state_len, action: Callable = None, color: tuple = (0, 0, 0)):
        """
        Args:
            bounding_box (BoundingBox): The bounding box of the widget.
            action (Callable, optional): The action to be executed when the widget is clicked. Defaults to None.
        """
        self.STATE_LEN = state_len
        self.action = action
        self.color = color
        super().__init__(self.STATE_LEN, bounding_box)

    def render(self, img: np.ndarray) -> np.ndarray:
        '''
        Renders the slider widget.
        '''
        thickness = -1
        color = self.color
        radius = 16

        # width, height of the square part of the checkbox
        width = self._bounding_box.width-2*radius
        # width, height of the square part of the checkbox
        height = int(self._bounding_box.height/2)

        x, y = self.get_bb().get_as_tuple()[0:2]
        # Modify x s.t. the radius of the circle is taken into account
        x += radius

        i = self.get_slider_value()

        # Draws a circle at the current state of the slider. Depending on the state, the circle will be drawn at a different position.
        cv2.circle(img, (x + (int(width/(self.STATE_LEN-1))*i)+10, y+height),
                   radius, color, thickness=thickness, lineType=cv2.LINE_AA)

        return img

    def handle_click(self, click_position: np.ndarray = None):
        '''
        Executes this slider action, if any.
        '''
        if self.has_click_action():
            self.action()

        self._state = np.roll(self.get_state(), 1)

    def has_click_action(self) -> bool:
        '''
        Returns whether or not this widget has a click action.
        '''
        if self.action is not None:
            return True
        return False

    def set_slider_value(self, state):
        '''
        Sets the state of the slider.
        '''
        self.get_state()[state] = 1

    def get_slider_value(self) -> int:
        '''
        Returns the state of the slider.
        '''
        return np.argmax(self.get_state())

    def reset(self):
        '''
        Resets the slider to the first state.
        '''
        self._state = np.zeros(self.STATE_LEN)
        # sets the first state to 1
        self._state[0] = 1
