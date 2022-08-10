import os
from typing import List, Optional

import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.enums import Base, Operator
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.utils import put_text
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem


class Calculator(Page):
    """The calculator page in the main-window. Always shows the last result.
    """

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "calculator.png")

    OPERAND_1_BB = BoundingBox(125, 316, 97, 22)
    OPERATOR_BB = BoundingBox(228, 316, 97, 22)
    OPERAND_2_BB = BoundingBox(331, 316, 97, 22)

    BUTTON_BB = BoundingBox(125, 406, 303, 22)
    # area adjusted to only show properties (bb does not match the grafical bb)
    RESULT_AREA_BB = BoundingBox(135, 48, 286, 183)

    def __init__(self):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        self.popup = CalculatorPopup(self)
        # init operator dropdown
        self.addition_ddi = DropdownItem(Operator.ADDITION, "+")
        self.subtraction_ddi = DropdownItem(Operator.SUBTRACTION, "-")
        self.multiplication_ddi = DropdownItem(Operator.MULTIPLICATION, "*")
        self.division_ddi = DropdownItem(Operator.DIVISION, "/")
        operator_ddis = [
            self.addition_ddi,
            self.subtraction_ddi,
            self.multiplication_ddi,
            self.division_ddi
        ]
        self.operator_dd = Dropdown(self.OPERATOR_BB, operator_ddis)
        self.operator_dd.set_selected_item(self.addition_ddi)
        # Set all operator dropdown items to invisible, 
        # the default visible ones will be set when initializing
        # the calculator settings class
        for operator_ddi in operator_ddis:
            self.operator_dd.set_visible(operator_ddi, 0)

        # create operand dropdowns
        self.operand_1_dd = self.create_operand_dd(self.OPERAND_1_BB)
        self.operand_2_dd = self.create_operand_dd(self.OPERAND_2_BB)

        self.dropdowns: List[Dropdown] = [self.operator_dd, self.operand_1_dd, self.operand_2_dd]
        self.add_widgets(self.dropdowns)

        self.base = Base.DECIMAL
        self.button = Button(self.BUTTON_BB, self.calculate)
        self.current_result = 0

    def set_operator_dd_item_visible(self, item: DropdownItem, visible: int):
        """Sets the given operator dropdown-item's visibility. Used by
        calculator-settings."""
        self.operator_dd.set_visible(item, visible)
        if visible:
            # update selected item when a new item becomes visible (always first item in dd list)
            self.operator_dd.set_selected_item(self.operator_dd.get_visible_items()[0])

    def create_operand_dd(self, bounding_box:BoundingBox) -> Dropdown:
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

    def set_base(self, base:Base) -> None:
        self.base = base

    def is_dropdown_open(self) -> bool:
        return self.get_opened_dropdown() is not None

    def get_opened_dropdown(self) -> Optional[Dropdown]:
        for dropdown in self.dropdowns:
            if dropdown.is_open():
                return dropdown
        return None

    def handle_click(self, click_position: np.ndarray = None):
        if self.popup.is_open():
            self.popup.handle_click(click_position)
            return

        opened_dd = self.get_opened_dropdown()
        if opened_dd is not None:
            opened_dd.handle_click(click_position)
            return

        for dropdown in self.dropdowns:
            if dropdown.is_clicked_by(click_position) or dropdown.is_open():
                dropdown.handle_click(click_position)
                return

        # needs to be called after dropdowns in case an opened dropdown occludes the button
        if self.button.is_clicked_by(click_position):
            self.button.handle_click()

    def is_popup_open(self) -> int:
        return self.popup.is_open()

    # Adopted from master-thesis code this app is based on.
    def calculate(self):
        operator: str = self.operator_dd.get_current_value().value
        a: int = self.operand_1_dd.get_current_value()
        b: int = self.operand_2_dd.get_current_value()
        output = None
        if operator == "+":
            output = a + b
        elif operator == "-":
            output = a - b
        elif operator == "*":
            output = a * b
        elif operator == "/":
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


class CalculatorPopup(Page):
    """Popup for the calculator (pops up when a division by zero is attempted).

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(87, 101, 234, 86)
    IMG_PATH = os.path.join(IMAGES_PATH, "calculator_popup.png")

    BUTTON_BB = BoundingBox(147, 143, 114, 22)

    def __init__(self, calculator:Calculator):
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        self.settings = calculator

        self.button: Button = Button(self.BUTTON_BB, self.close)

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.button.is_clicked_by(click_position):
            self.button.handle_click()

    def open(self):
        """Opens this popup."""
        self.get_state()[0] = 1

    def close(self):
        """Closes this popup."""
        self.get_state()[0] = 0

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]
