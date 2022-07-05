import cv2
import numpy as np

from typing import Callable, List
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.colors import Color
from naturalnets.environments.app.exception import ArgumentError
from naturalnets.environments.app.page import Widget
from naturalnets.environments.app.utils import get_group_bounding_box

class RadioButton(Widget):

    STATE_LEN = 1

    def __init__(self, bounding_box:BoundingBox, value=None, action:Callable=None):
        super().__init__(self.STATE_LEN, bounding_box)
        self._action = action
        self._value = value

    def handle_click(self):
        if self.has_click_action():
            self._action()

    def set_selected(self, selected:bool):
        self.get_state()[0] = selected

    def is_selected(self):
        return self.get_state()[0]

    def has_click_action(self):
        return self._action is not None

    def get_value(self):
        return self._value

    def render(self, img: np.ndarray) -> np.ndarray:
        circle_width = circle_height = 14
        if self.is_selected():
            x, y = self.get_bb().get_as_tuple()[0:2]
            c_x = x + circle_width//2
            c_y = y + circle_height//2
            radius = min(circle_width, circle_height)//4
            color = Color.BLACK.value
            thickness = -1
            cv2.circle(img, (c_x, c_y), radius, color ,thickness)
        return img


class RadioButtonGroup(Widget):

    STATE_LEN = 0
    BOUNDING_BOX = BoundingBox(0, 0, 0, 0)

    def __init__(self, radio_buttons:List[RadioButton]):
        """Instantiates a RadioButtonGroup with at least one RadioButton. The
        first RadioButton in radio_buttons is initially selected.

        Args:
            radio_buttons (List[RadioButton]): Initial RadioButtons for this group. 
            len(radio_buttons) >= 1.

        Raises:
            ArgumentError: If len(radio_buttons) < 1
        """
        if len(radio_buttons) < 1:
            raise ArgumentError("RadioButtonGroup must be instantiated with at least one RadioButton.")
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX)

        self.radio_buttons:list[RadioButton] = []
        self.add_radio_buttons(radio_buttons)
        self.set_selected_button(radio_buttons[0])
        
    def add_radio_button(self, radio_button:RadioButton):
        self.add_child(radio_button)
        self.radio_buttons.append(radio_button)
        self.set_bb(get_group_bounding_box(self.radio_buttons))

    def add_radio_buttons(self, radio_buttons:List[RadioButton]):
        for radio_button in radio_buttons:
            self.add_radio_button(radio_button)
        
    def handle_click(self, click_position:np.ndarray):
        """If click_position hits a radio button in this group, selects the 
        radio button if it has no click-action. Otherwise the click action is
        executed without changing the current selection.

        Args:
            click_position (np.ndarray): the position of the click
        """
        for radio_button in self.radio_buttons:
            if radio_button.is_clicked_by(click_position):
                if radio_button.has_click_action():
                    radio_button.handle_click()
                else:
                    self.set_selected_button(radio_button)

    def set_selected_button(self, selected_button:RadioButton):
        for radio_button in self.radio_buttons:
            if radio_button == selected_button:
                radio_button.set_selected(True)
                self._selected_radio_button = radio_button
            else:
                radio_button.set_selected(False)

    def get_selected_radio_button(self) -> RadioButton:
        return self._selected_radio_button

    def get_value(self):
        return self._selected_radio_button.get_value()

    def render(self, img: np.ndarray) -> np.ndarray:
        self._selected_radio_button.render(img)
        return img



