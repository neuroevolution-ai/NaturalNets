
from typing import Callable, List
import cv2

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.exception import ArgumentError
from naturalnets.environments.gui_app.page import Widget
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton


class Textfield(Widget):
    '''
    A textfield widget. This widget is a like radio button that can be selected and deselected.

    State Description:
        0: Whether or not the textfield is selected
    '''
    #Constants
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

    def has_click_action(self) -> bool:
        '''
        Returns whether or not this widget has a click action.
        '''
        return self._click_action is not None

    def set_selected(self, selected: int):
        '''
        Sets the state of the textfield.
        '''
        self.get_state()[0] = selected

    def is_selected(self) -> int:
        '''
        Returns the state of the textfield.
        '''
        return self.get_state()[0]

    def enter_value(self):
        '''
        This function is called when the textfield is clicked.
        '''
        if (self.is_selected()):
            self.set_selected(False)
        else:
            self.set_selected(True)

    def render(self, img: np.ndarray) -> np.ndarray:
        '''
        Renders the textfield onto the given image.
        '''

        if self.is_selected():
            width = self._bounding_box.width
            height = int(self._bounding_box.height)
            
            int  # width, height of the square part of the checkbox
            thickness = 2
            color = (96, 134, 247)
            text = "Sample Text for Textfield"
            font = cv2.FONT_HERSHEY_SIMPLEX

            text_size, _ = cv2.getTextSize(text, font, 1, thickness)
            text_height = text_size[1]
            text_width = text_size[0]
            x, y = self.get_bb().get_as_tuple()[0:2]

            # change allignment of text
            x = x + 25
            y = y + 10
            cv2.rectangle(img, (x, int(y+height/2)+10), (x + text_width, y+text_height-10), color=(255,255,255), thickness=-1) 
            cv2.putText(img, text, (x, int(y+height/2)), font, 1, color=color, thickness=thickness)
            
        return img

    def reset(self):
        '''
        This function is called to reset the textfield.
        '''
        self.set_selected(False)
