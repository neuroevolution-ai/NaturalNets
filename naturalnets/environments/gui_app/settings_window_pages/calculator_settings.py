import os
from typing import List, Optional, Tuple

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.gui_app.enums import Base
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.main_window_pages.calculator import Calculator, Operator
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem


class CalculatorSettings(Page, RewardElement):
    """The calculator settings page, manipulates the calculator page."""
    STATE_LEN = 0
    MAX_CLICKABLE_ELEMENTS = 5

    IMG_PATH = os.path.join(IMAGES_PATH, "calculator_settings.png")

    ADDITION_BB = BoundingBox(38, 117, 66, 14)
    MULTIPLICATION_BB = BoundingBox(38, 143, 91, 14)
    SUBTRACTION_BB = BoundingBox(217, 117, 83, 14)
    DIVISION_BB = BoundingBox(217, 143, 65, 14)

    BASE_DD_BB = BoundingBox(217, 220, 173, 22)

    def __init__(self, calculator: Calculator):
        Page.__init__(self, self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.calculator = calculator

        self.addition = CheckBox(
            self.ADDITION_BB,
            lambda is_checked: self.calculator.set_operator_dd_item_visible(
                self.calculator.addition_ddi, is_checked
            )
        )
        self.subtraction = CheckBox(
            self.SUBTRACTION_BB,
            lambda is_checked: self.calculator.set_operator_dd_item_visible(
                self.calculator.subtraction_ddi, is_checked
            )
        )
        self.multiplication = CheckBox(
            self.MULTIPLICATION_BB,
            lambda is_checked: self.calculator.set_operator_dd_item_visible(
                self.calculator.multiplication_ddi, is_checked
            )
        )
        self.division = CheckBox(
            self.DIVISION_BB,
            lambda is_checked: self.calculator.set_operator_dd_item_visible(
                self.calculator.division_ddi, is_checked
            )
        )

        self.operator_checkboxes = [
            self.addition,
            self.subtraction,
            self.multiplication,
            self.division
        ]
        self.add_widgets(self.operator_checkboxes)

        self.operator_to_checkbox = {
            Operator.ADDITION: self.addition,
            Operator.SUBTRACTION: self.subtraction,
            Operator.MULTIPLICATION: self.multiplication,
            Operator.DIVISION: self.division,
        }

        self.base_10_ddi = DropdownItem(Base.DECIMAL, "Base 10")
        self.base_2_ddi = DropdownItem(Base.BINARY, "Base 2")
        self.base_16_ddi = DropdownItem(Base.HEX, "Base 16")
        self.dropdown = Dropdown(self.BASE_DD_BB, [self.base_10_ddi,
                                                   self.base_2_ddi,
                                                   self.base_16_ddi])
        self.add_widget(self.dropdown)

        self.opened_dd: Optional[Dropdown] = None

        self.popup = CalculatorSettingsPopup(self)
        self.add_child(self.popup)

        self.set_reward_children([self.popup])

    @property
    def reward_template(self):
        return {
            "base_dropdown_opened": 0
        }

    def reset(self):
        self.popup.close()
        self.popup.reset()

        self.dropdown.close()
        self.dropdown.set_selected_item(self.base_10_ddi)
        self.addition.set_selected(1)
        self.subtraction.set_selected(1)
        self.multiplication.set_selected(0)
        self.division.set_selected(0)

    def handle_click(self, click_position: np.ndarray):
        if self.is_popup_open():
            self.popup.handle_click(click_position)
            return

        # Handle the case of an opened dropdown first
        if self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)
            self.calculator.set_base(self.dropdown.get_current_value())
            self.opened_dd = None
            return

        if self.dropdown.is_clicked_by(click_position):
            self.dropdown.handle_click(click_position)

            if self.dropdown.is_open():
                self.opened_dd = self.dropdown

                self.register_selected_reward(["base_dropdown_opened"])
            return

        for checkbox in self.operator_checkboxes:
            if checkbox.is_clicked_by(click_position):
                checkbox.handle_click(click_position)
                break

        # Open popup if click deselected last selected checkbox
        if self.get_selected_checkboxes_count() == 0:
            self.popup.open()

    def find_nearest_clickable(self, click_position: np.ndarray, current_minimal_distance: float,
                               current_clickable: Clickable) -> Tuple[float, Clickable, np.ndarray]:

        current_minimal_distance, current_clickable, popup_click_position = self.popup.find_nearest_clickable(
            click_position, current_minimal_distance, current_clickable
        )

        if self.is_popup_open():
            # Open popup overlaps the checkboxes on the right completely
            clickable_checkboxes = [self.addition, self.multiplication]
        else:
            clickable_checkboxes = self.operator_checkboxes

        for checkbox in clickable_checkboxes:
            current_minimal_distance, current_clickable = checkbox.calculate_distance_to_click(
                click_position, current_minimal_distance, current_clickable
            )

        current_minimal_distance, current_clickable = self.dropdown.calculate_distance_to_click(
            click_position, current_minimal_distance, current_clickable
        )

        return current_minimal_distance, current_clickable, current_clickable.get_bb().get_click_point_inside_bb()

    def get_selected_checkboxes_count(self) -> int:
        """Returns the number of selected checkboxes."""
        return sum(checkbox.is_selected() for checkbox in self.operator_checkboxes)

    def is_popup_open(self) -> bool:
        return bool(self.popup.is_open())

    def is_dropdown_open(self) -> bool:
        return self.opened_dd is not None

    def select_operator_checkbox(self, operator: Operator):
        """Selects the checkbox corresponding to the given operator (used by popup)."""
        self.operator_to_checkbox[operator].set_selected(1)

    def render(self, img: np.ndarray):
        """Renders the calculator settings as well as its popup (if opened) onto the given image."""
        img = super().render(img)
        if self.popup.is_open():
            img = self.popup.render(img)
        return img

    def get_clickable_elements(self, clickable_elements: List[Clickable]) -> List[Clickable]:
        if self.popup.is_open():
            return self.popup.get_clickable_elements()

        if self.opened_dd is not None:
            return self.opened_dd.get_visible_items()

        clickable_elements.extend(self.operator_checkboxes)
        clickable_elements.append(self.dropdown)

        return clickable_elements


class CalculatorSettingsPopup(Page, RewardElement):
    """Popup for the calculator settings (pops up when no operator-checkbox is selected).

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1
    MAX_CLICKABLE_ELEMENTS = 2

    BOUNDING_BOX = BoundingBox(47, 87, 315, 114)
    IMG_PATH = os.path.join(IMAGES_PATH, "calculator_settings_popup.png")

    DROPDOWN_BB = BoundingBox(69, 129, 271, 22)
    APPLY_BUTTON_BB = BoundingBox(123, 157, 163, 22)

    def __init__(self, calculator_settings: CalculatorSettings):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.apply_button = Button(self.APPLY_BUTTON_BB, self.close)
        self.calculator_settings = calculator_settings

        self.addition_ddi = DropdownItem(Operator.ADDITION, "Addition")
        self.subtraction_ddi = DropdownItem(Operator.SUBTRACTION, "Subtraction")
        self.multiplication_ddi = DropdownItem(Operator.MULTIPLICATION, "Multiplication")
        self.division_ddi = DropdownItem(Operator.DIVISION, "Division")
        self.dropdown = Dropdown(self.DROPDOWN_BB, [self.addition_ddi,
                                                    self.subtraction_ddi,
                                                    self.multiplication_ddi,
                                                    self.division_ddi])
        self.add_widget(self.dropdown)

        self.dropdown_opened = False

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"],
            "operator_dropdown_opened": 0,
            "operator_selection": [
                Operator.ADDITION,
                Operator.SUBTRACTION,
                Operator.MULTIPLICATION,
                Operator.DIVISION
            ]
        }

    def reset(self):
        self.dropdown.close()
        self.dropdown_opened = False

        self.dropdown.set_selected_item(self.addition_ddi)

    def handle_click(self, click_position: np.ndarray = None) -> None:
        # Check dropdown first, may obscure apply-button when opened
        if self.dropdown_opened:
            self.dropdown.handle_click(click_position)

            self.register_selected_reward(["operator_selection", self.dropdown.get_current_value()])

            self.dropdown_opened = False
            return

        if self.dropdown.is_clicked_by(click_position):
            self.dropdown.handle_click(click_position)

            if self.dropdown.is_open():
                self.dropdown_opened = True
                self.register_selected_reward(["operator_dropdown_opened"])
            return

        if self.apply_button.is_clicked_by(click_position):
            curr_dropdown_value: Operator = self.dropdown.get_current_value()
            assert curr_dropdown_value is not None
            self.apply_button.handle_click(click_position)
            self.calculator_settings.select_operator_checkbox(curr_dropdown_value)
            self.calculator_settings.calculator.set_operator_value(curr_dropdown_value)

    def find_nearest_clickable(self, click_position: np.ndarray, current_minimal_distance: float,
                               current_clickable: Clickable) -> Tuple[float, Clickable, np.ndarray]:
        if self.is_open():
            current_minimal_distance, current_clickable = self.dropdown.calculate_distance_to_click(
                click_position, current_minimal_distance, current_clickable
            )

            if not self.dropdown.is_open():
                current_minimal_distance, current_clickable = self.apply_button.calculate_distance_to_click(
                    click_position, current_minimal_distance, current_clickable
                )

            return current_minimal_distance, current_clickable, current_clickable.get_bb().get_click_point_inside_bb()

        return current_minimal_distance, current_clickable, click_position

    def open(self):
        """Opens this popup."""
        self.get_state()[0] = 1
        self.dropdown.set_selected_item(self.addition_ddi)

        self.register_selected_reward(["popup", "open"])

    def close(self):
        """Closes this popup."""
        self.get_state()[0] = 0

        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]

    def get_clickable_elements(self) -> List[Clickable]:
        if self.dropdown_opened:
            return self.dropdown.get_visible_items()

        return [self.dropdown, self.apply_button]
