import os
from typing import List

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.gui_app.enums import Base, Operator
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem


class Calculator(Page, RewardElement):
    """The calculator page in the main-window. Always shows the last result.
    """

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "calculator.png")

    OPERAND_1_BB = BoundingBox(125, 316, 97, 22)
    OPERATOR_BB = BoundingBox(228, 316, 97, 22)
    OPERAND_2_BB = BoundingBox(331, 316, 97, 22)

    BUTTON_BB = BoundingBox(125, 406, 303, 22)
    # Area adjusted to only show properties (bb does not match the graphical bb)
    RESULT_AREA_BB = BoundingBox(135, 48, 286, 183)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.popup = CalculatorPopup()
        self.add_child(self.popup)

        self.addition_ddi = DropdownItem(Operator.ADDITION, "+")
        self.subtraction_ddi = DropdownItem(Operator.SUBTRACTION, "-")
        self.multiplication_ddi = DropdownItem(Operator.MULTIPLICATION, "*")
        self.division_ddi = DropdownItem(Operator.DIVISION, "/")

        self.operator_ddis = [
            self.addition_ddi,
            self.subtraction_ddi,
            self.multiplication_ddi,
            self.division_ddi
        ]

        self.operator_dd = Dropdown(self.OPERATOR_BB, self.operator_ddis)

        self.operator_ddis_to_str = {
            self.addition_ddi: "addition_operator",
            self.subtraction_ddi: "subtraction_operator",
            self.multiplication_ddi: "multiplication_operator",
            self.division_ddi: "division_operator"
        }

        # Create operand dropdowns
        self.operand_1_dd = self.create_operand_dd(self.OPERAND_1_BB)
        self.operand_2_dd = self.create_operand_dd(self.OPERAND_2_BB)

        self.dropdowns: List[Dropdown] = [self.operator_dd, self.operand_1_dd, self.operand_2_dd]

        self.add_widgets(self.dropdowns)

        self.dropdowns_to_str = {
            self.operand_1_dd: "first_operand_dropdown",
            self.operand_2_dd: "second_operand_dropdown",
            self.operator_dd: "operator_dropdown",
        }

        # Does not need to be added as child, because buttons do not have a state
        self.button = Button(self.BUTTON_BB, self.calculate)

        self.opened_dd = None
        self.base = None
        self.current_result = None

        self.set_reward_children([self.popup])

    @property
    def reward_template(self):
        return {
            "first_operand_dropdown": {
                "opened": 0,
                "selected": [0, 1, 2, 3, 4],
                "used_in_calculate": [0, 1, 2, 3, 4]
            },
            "second_operand_dropdown": {
                "opened": 0,
                "selected": [0, 1, 2, 3, 4],
                "used_in_calculate": [0, 1, 2, 3, 4]
            },
            "operator_dropdown": {
                "opened": 0,
                "selected": [
                    Operator.ADDITION, Operator.SUBTRACTION, Operator.MULTIPLICATION, Operator.DIVISION
                ],
                "used_in_calculate": [
                    Operator.ADDITION, Operator.SUBTRACTION, Operator.MULTIPLICATION, Operator.DIVISION
                ]
            },
            "addition_operator_setting": [False, True],
            "subtraction_operator_setting": [False, True],
            "multiplication_operator_setting": [False, True],
            "division_operator_setting": [False, True],
            "numeral_system": [Base.DECIMAL, Base.BINARY, Base.HEX],
            "numeral_system_setting": [Base.DECIMAL, Base.BINARY, Base.HEX]
        }

    def reset(self):
        self.popup.close()

        self.operator_dd.close()
        self.operand_1_dd.close()
        self.operand_2_dd.close()

        self.opened_dd = None
        self.base = Base.DECIMAL
        self.current_result = 0

        self.operator_dd.set_selected_item(self.addition_ddi)

        self.addition_ddi.set_visible(1)
        self.subtraction_ddi.set_visible(1)
        self.multiplication_ddi.set_visible(0)
        self.division_ddi.set_visible(0)

    def set_operator_dd_item_visible(self, item: DropdownItem, visible: int):
        """Sets the given operator dropdown-item's visibility. Used by
        calculator-settings."""
        item.set_visible(visible)

        self.register_selected_reward([self.operator_ddis_to_str[item] + "_setting", bool(visible)])

        if visible:
            # Update selected item when a new item becomes visible (always first item in dd list)
            self.operator_dd.set_selected_item(self.operator_dd.get_visible_items()[0])

    def create_operand_dd(self, bounding_box: BoundingBox) -> Dropdown:
        """Creates the operand dropdown."""
        first_item = DropdownItem(0, "0")
        ddis = [
            first_item,
            DropdownItem(1, "1"),
            DropdownItem(2, "2"),
            DropdownItem(3, "3"),
            DropdownItem(4, "4")
        ]
        dropdown = Dropdown(bounding_box, ddis)
        dropdown.set_selected_item(first_item)
        return dropdown

    def set_base(self, base: Base) -> None:
        self.base = base

        self.register_selected_reward(["numeral_system_setting", base])

    def is_dropdown_open(self) -> bool:
        return self.opened_dd is not None

    def handle_click(self, click_position: np.ndarray):
        if self.popup.is_open():
            self.popup.handle_click(click_position)
            return

        if self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)

            current_value = self.opened_dd.get_current_value()
            self.register_selected_reward([self.dropdowns_to_str[self.opened_dd], "selected", current_value])

            self.opened_dd = None
            return

        for dropdown in self.dropdowns:
            if dropdown.is_clicked_by(click_position):
                dropdown.handle_click(click_position)

                if dropdown.is_open():
                    self.opened_dd = dropdown
                    self.register_selected_reward([self.dropdowns_to_str[dropdown], "opened"])
                return

        # Needs to be called _after_ the dropdowns, in case an opened dropdown occludes the button
        if self.button.is_clicked_by(click_position):
            self.button.handle_click(click_position)

    def set_operator_value(self, value: Operator):
        self.operator_dd.set_selected_value(value)

    def is_popup_open(self) -> int:
        return self.popup.is_open()

    # Adopted from master-thesis code this app is based on.
    def calculate(self):
        operator = self.operator_dd.get_current_value()
        operator_str = operator.value
        a: int = self.operand_1_dd.get_current_value()
        b: int = self.operand_2_dd.get_current_value()

        self.register_selected_reward(["numeral_system", self.base])
        self.register_selected_reward([self.dropdowns_to_str[self.operator_dd], "used_in_calculate", operator])
        self.register_selected_reward([self.dropdowns_to_str[self.operand_1_dd], "used_in_calculate", a])
        self.register_selected_reward([self.dropdowns_to_str[self.operand_2_dd], "used_in_calculate", b])

        output = None
        if operator_str == "+":
            output = a + b
        elif operator_str == "-":
            output = a - b
        elif operator_str == "*":
            output = a * b
        elif operator_str == "/":
            try:
                output = a / b
            except ZeroDivisionError:
                self.popup.open()
                return
        assert output is not None
        self.current_result = output

    def render(self, img: np.ndarray):
        vertical_space = 20
        img = super().render(img)
        if self.popup.is_open():
            img = self.popup.render(img)
        x, y, _, height = self.RESULT_AREA_BB.get_as_tuple()
        bottom_left_corner = (x, y + height)
        put_text(img, f"{self.base}", bottom_left_corner, font_scale=0.4)
        bottom_left_corner = (x, y + height - vertical_space)
        put_text(img, f"Last result: {self.current_result}", bottom_left_corner, font_scale=0.4)

        return img


class CalculatorPopup(Page, RewardElement):
    """Popup for the calculator (pops up when a division by zero is attempted).

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(87, 101, 234, 86)
    IMG_PATH = os.path.join(IMAGES_PATH, "calculator_popup.png")

    BUTTON_BB = BoundingBox(147, 143, 114, 22)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.button: Button = Button(self.BUTTON_BB, self.close)

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.button.is_clicked_by(click_position):
            self.button.handle_click(click_position)

    def open(self):
        """Opens this popup."""
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close(self):
        """Closes this popup."""
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]
