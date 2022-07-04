from enum import Enum
from typing import List
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem

class Base(Enum):
    DECIMAL = 0
    BINARY = 2
    HEX = 16

class Operator(Enum):
    ADDITION = "+"
    SUBTRACTION = "-"
    MULTIPLICATION = "*"
    DIVISION = "/"

class Calculator(Page):

    STATE_LEN = 0
    IMG_PATH = IMAGES_PATH + "calculator.png"

    OPERAND_1_BB = BoundingBox(125, 316, 97, 22)
    OPERATOR_BB = BoundingBox(228, 316, 97, 22)
    OPERAND_2_BB = BoundingBox(331, 316, 97, 22)

    BUTTON_BB = BoundingBox(125, 406, 303, 22)

    def __init__(self):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        # init operator dropdown
        self.addition_ddi = DropdownItem(Operator.ADDITION, "+")
        self.subtraction_ddi = DropdownItem(Operator.SUBTRACTION, "-")
        self.multiplication_ddi = DropdownItem(Operator.MULTIPLICATION, "*")
        self.division_ddi = DropdownItem(Operator.DIVISION, "/")
        operator_ddis = [self.addition_ddi, self.subtraction_ddi, self.multiplication_ddi, self.division_ddi]
        self.operator_dd = Dropdown(self.OPERATOR_BB, operator_ddis)
        self.operator_dd.set_selected_item(self.addition_ddi)
        # set all operator droddown items to invisible, visible ones will be set through calculator settings
        for operator_ddi in operator_ddis:
            self.operator_dd.set_visible(operator_ddi, False)
            

        # create operand dropdowns
        self.operand_1_dd = self.create_operand_dd(self.OPERAND_1_BB)
        self.operand_2_dd = self.create_operand_dd(self.OPERAND_2_BB)

        self.dropdowns:List[Dropdown] = [self.operator_dd, self.operand_1_dd, self.operand_2_dd]
        self.add_widgets(self.dropdowns)

        self.base = Base.DECIMAL
        self.button = Button(self.BUTTON_BB, lambda: self.calculate())

    def set_operator_dd_item_visible(self, item, visible):
        self.operator_dd.set_visible(item, visible)
        if visible == True:
            # update selected item when a new item becomes visible (always first item in dd list)
            self.operator_dd.set_selected_item(self.operator_dd.get_visible_items()[0])

    def create_operand_dd(self, bounding_box:BoundingBox) -> List[DropdownItem]:
        first_item = DropdownItem(0, "0")
        ddis = [first_item,
                DropdownItem(1, "1"),
                DropdownItem(2, "2"),
                DropdownItem(3, "3"),
                DropdownItem(4, "4"),]
        dd = Dropdown(bounding_box, ddis)
        dd.set_selected_item(first_item)
        return dd
        
    def set_base(self, base:Base) -> None:
        self.base = base

    def is_dropdown_open(self):
        return self.get_opened_dropdown() is not None

    def get_opened_dropdown(self) -> Dropdown:
        for dropdown in self.dropdowns:
            if dropdown.is_open():
                return dropdown
        return None

    def handle_click(self, click_position: np.ndarray = None):
        opened_dd = self.get_opened_dropdown()
        if opened_dd is not None:
            opened_dd.handle_click(click_position)
            return
        else: 
            for dropdown in self.dropdowns:
                if dropdown.is_clicked_by(click_position) or dropdown.is_open():
                    dropdown.handle_click(click_position)
                    return

        # needs to be called after dropdowns in case an opened dropdown occludes the button
        if self.button.is_clicked_by(click_position):
            self.button.handle_click()

    def calculate(self):
        # TODO(maybe): not needed for neural net training, 
        # may be implemented if desired for rendering
        pass

