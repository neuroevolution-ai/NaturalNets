from typing import Any, Callable, List

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.gui_app.exception import ArgumentError
from naturalnets.environments.gui_app.page import Widget
from naturalnets.environments.gui_app.utils import get_group_bounding_box


class RadioButton(Widget):
    """Widget representing a single RadioButton. Every RadioButton
    needs to be part of a RadioButtonGroup, which handles the
    selected-state of all its RadioButtons.

       State description:
            state[0]: the selected-state of this RadioButton.
    """

    STATE_LEN = 1

    def __init__(self, bounding_box: BoundingBox, value: Any = None, action: Callable = None):
        """
        Args:
            bounding_box (BoundingBox): The BoundingBox of this Widget.
            value (Any, optional): The value that this RadioButton represents. Defaults to None.
            action (Callable, optional): The action performed when calling handle_click().
            Defaults to None.
        """
        super().__init__(self.STATE_LEN, bounding_box)
        self._action = action
        self._value = value

    def handle_click(self, click_position: np.ndarray = None) -> None:
        """ Executes this RadioButtons action, if any.

        Args:
            click_position (np.ndarray, optional): Not used. Defaults to None.
        """
        if self.has_click_action():
            self._action()

    def set_selected(self, selected: int):
        self.get_state()[0] = selected

    def is_selected(self) -> int:
        return self.get_state()[0]

    def has_click_action(self):
        return self._action is not None

    def get_value(self):
        return self._value

    def render(self, img: np.ndarray) -> np.ndarray:
        circle_width = circle_height = 14
        if self.is_selected():
            x, y = self.get_bb().get_as_tuple()[0:2]
            c_x = x + circle_width // 2
            c_y = y + circle_height // 2
            radius = min(circle_width, circle_height) // 4
            color = Color.BLACK.value
            thickness = -1
            cv2.circle(img, (c_x, c_y), radius, color, thickness)
        return img


class RadioButtonGroup(Widget):
    """Widget representing a RadioButtonGroup. Handles the selected-state of
       its RadioButtons (see handle_click()).

       State description:
            Has no inherent state, the state is made up of the state from it's RadioButtons.
    """

    STATE_LEN = 0
    BOUNDING_BOX = BoundingBox(0, 0, 0, 0)

    def __init__(self, radio_buttons: List[RadioButton]):
        """Instantiates a RadioButtonGroup with at least one RadioButton. The
        first RadioButton in radio_buttons is initially selected.

        Args:
            radio_buttons (List[RadioButton]): Initial RadioButtons for this group.
            len(radio_buttons) >= 1.

        Raises:
            ArgumentError: If len(radio_buttons) < 1
        """
        if len(radio_buttons) < 1:
            error_msg: str = "RadioButtonGroup must be instantiated with at least one RadioButton."
            raise ArgumentError(error_msg)
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX)

        self.radio_buttons: List[RadioButton] = []
        self.add_radio_buttons(radio_buttons)
        self._selected_radio_button = None
        self.set_selected_button(radio_buttons[0])

    def add_radio_button(self, radio_button: RadioButton):
        self.add_child(radio_button)
        self.radio_buttons.append(radio_button)
        self.set_bb(get_group_bounding_box(self.radio_buttons))

    def add_radio_buttons(self, radio_buttons: List[RadioButton]):
        for radio_button in radio_buttons:
            self.add_radio_button(radio_button)

    def handle_click(self, click_position: np.ndarray) -> None:
        """If click_position hits a radio button in this group, check if it has a click action.
        If so, run the click action. Otherwise, simply select the radio button. A click action
        can be for example a confirmation dialog, if that particular radio button shall indeed
        be selected.

        Args:
            click_position (np.ndarray): the position of the click.
        """
        for radio_button in self.radio_buttons:
            if radio_button.is_clicked_by(click_position):
                if radio_button.has_click_action():
                    radio_button.handle_click()
                else:
                    self.set_selected_button(radio_button)

                return

    def set_selected_button(self, selected_button: RadioButton):
        """Selects the given RadioButton and deselects all others.

        Args:
            selected_button (RadioButton): RadioButton to be selected, must be part of this
            RadioButtonGroup.
        """
        if self._selected_radio_button is not None:
            self._selected_radio_button.set_selected(0)
        selected_button.set_selected(1)
        self._selected_radio_button = selected_button

    def get_selected_radio_button(self) -> RadioButton:
        return self._selected_radio_button

    def get_value(self):
        """Returns the value of the currently selected RadioButton.
        """
        return self._selected_radio_button.get_value()

    def render(self, img: np.ndarray) -> np.ndarray:
        self._selected_radio_button.render(img)
        return img
