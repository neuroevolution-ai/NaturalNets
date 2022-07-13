import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.enums import Base
from naturalnets.environments.app.main_window_pages.calculator import Calculator, Operator
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.check_box import CheckBox
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem

class CalculatorSettings(Page):
    STATE_LEN = 0
    IMG_PATH = IMAGES_PATH + "calculator_settings.png"

    ADDITION_BB = BoundingBox(38, 117, 66, 14)
    MULTIPLICATION_BB = BoundingBox(38, 143, 91, 14)
    SUBTRACTION_BB = BoundingBox(217, 117, 83, 14)
    DIVISION_BB = BoundingBox(217, 143, 65, 14)

    BASE_DD_BB = BoundingBox(217, 220, 173, 22)

    def __init__(self, calculator:Calculator):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        self.calculator = calculator

        self.addition = CheckBox(self.ADDITION_BB, 
            lambda is_checked: self.calculator.set_operator_dd_item_visible(self.calculator.addition_ddi, is_checked))
        self.subtraction = CheckBox(self.SUBTRACTION_BB, 
            lambda is_checked: self.calculator.set_operator_dd_item_visible(self.calculator.subtraction_ddi, is_checked))
        self.multiplication = CheckBox(self.MULTIPLICATION_BB, 
            lambda is_checked: self.calculator.set_operator_dd_item_visible(self.calculator.multiplication_ddi, is_checked))
        self.division = CheckBox(self.DIVISION_BB, 
            lambda is_checked: self.calculator.set_operator_dd_item_visible(self.calculator.division_ddi, is_checked))

        self.operator_checkboxes = [self.addition, self.subtraction, self.multiplication, self.division]
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
        self.dropdown = Dropdown(self.BASE_DD_BB, [self.base_10_ddi, self.base_2_ddi, self.base_16_ddi])
        self.add_widget(self.dropdown)

        self.popup = CalculatorSettingsPopup(self)

        # initial state
        self.dropdown.set_selected_item(self.base_10_ddi)
        self.addition.set_selected(True)
        self.subtraction.set_selected(True)

    def handle_click(self, click_position: np.ndarray):
        if self.is_popup_open():
            self.popup.handle_click(click_position)
        elif self.dropdown.is_clicked_by(click_position) or self.is_dropdown_open():
            self.dropdown.handle_click(click_position)
            self.calculator.set_base(self.dropdown.get_current_value())
        else:
            for checkbox in self.operator_checkboxes:
                if checkbox.is_clicked_by(click_position):
                    checkbox.handle_click(click_position)
                    break
            if self.get_selected_checkboxes_count() == 0:
                self.popup.open()

    def get_selected_checkboxes_count(self) -> int:
        sum = 0
        for checkbox in self.operator_checkboxes:
            sum += checkbox.is_selected()
        return sum

    def is_popup_open(self) -> bool:
        return self.popup.is_open()

    def is_dropdown_open(self) -> bool:
        return self.dropdown.is_open()

    def select_operator_checkbox(self, operator:Operator):
        self.operator_to_checkbox[operator].set_selected(True)

    def render(self, img: np.ndarray):
        img = super().render(img)
        if self.popup.is_open():
            img = self.popup.render(img)
        return img

class CalculatorSettingsPopup(Page):
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(47, 87, 315, 114)
    IMG_PATH = IMAGES_PATH + "calculator_settings_popup.png"

    DROPDOWN_BB = BoundingBox(69, 129, 271, 22)
    APPLY_BUTTON_BB = BoundingBox(123, 157, 163, 22)

    def __init__(self, calculator_settings:CalculatorSettings):
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        self.apply_button = Button(self.APPLY_BUTTON_BB, lambda: self.close())
        self.calculator_settings = calculator_settings

        self.addition_ddi = DropdownItem(Operator.ADDITION, "Addition")
        self.subtraction_ddi = DropdownItem(Operator.SUBTRACTION, "Subtraction")
        self.multiplication_ddi = DropdownItem(Operator.MULTIPLICATION, "Multiplication")
        self.division_ddi = DropdownItem(Operator.DIVISION, "Division")
        self.dropdown = Dropdown(self.DROPDOWN_BB, [self.addition_ddi, self.subtraction_ddi, self.multiplication_ddi, self.division_ddi])
        self.add_widget(self.dropdown)

    def handle_click(self, click_position: np.ndarray = None) -> None:
        # check dropdown first, may obscure apply-button when opened
        if self.dropdown.is_clicked_by(click_position) or self.dropdown.is_open():
            self.dropdown.handle_click(click_position)
        elif self.apply_button.is_clicked_by(click_position):
            self.apply_button.handle_click()
            curr_dropdown_value:str = self.dropdown.get_current_value()
            if curr_dropdown_value is not None:
                self.calculator_settings.select_operator_checkbox(curr_dropdown_value)
                self.calculator_settings.calculator.operator_dd.set_selected_value(curr_dropdown_value)

    def open(self):
        self.get_state()[0] = 1
        self.dropdown.set_selected_item(self.addition_ddi)

    def close(self):
        self.get_state()[0] = 0

    def is_open(self):
        return self.get_state()[0]