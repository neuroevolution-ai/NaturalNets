import itertools
import numpy as np

from typing import List
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.interfaces import HasPopups
from naturalnets.environments.app.main_window_pages.car_configurator import CarConfigurator
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.utils import get_group_bounding_box
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.check_box import CheckBox


class CarConfiguratorSettings(Page):
    STATE_LEN = 0
    IMG_PATH = IMAGES_PATH + "car_configurator_settings.png"

    TIRE_20_INCH_BB = BoundingBox(48, 73, 83, 14)
    TIRE_22_INCH_BB = BoundingBox(48, 99, 83, 14)
    TIRE_18_INCH_BB = BoundingBox(217, 73, 83, 14)
    TIRE_19_INCH_BB = BoundingBox(217, 99, 83, 14)

    INTERIOR_MODERN_BB = BoundingBox(48, 146, 104, 14)
    INTERIOR_VINTAGE_BB = BoundingBox(48, 172, 104, 14)
    INTERIOR_SPORT_BB = BoundingBox(217, 146, 91, 14)

    COMBUSTION_ENGINE_A_BB = BoundingBox(48, 219, 139, 14)
    COMBUSTION_ENGINE_B_BB = BoundingBox(48, 245, 139, 14)
    COMBUSTION_ENGINE_C_BB = BoundingBox(48, 271, 139, 14)

    ELECTRIC_MOTOR_A_BB = BoundingBox(270, 219, 106, 14)
    ELECTRIC_MOTOR_B_BB = BoundingBox(270, 245, 106, 14)

    def __init__(self, car_configurator:CarConfigurator):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        self.car_configurator = car_configurator

        # add popup window as child
        self.car_disabled_popup = CarDisabledPopup()
        self.add_child(self.car_disabled_popup)

        # configure checkboxes
        self._tire_checkboxes = self._get_tire_checkboxes()
        self.add_widgets(self._tire_checkboxes)

        self._interior_checkboxes = self._get_interior_checkboxes()
        self.add_widgets(self._interior_checkboxes)

        self._motor_checkboxes = self._get_motor_checkboxes()
        self.add_widgets(self._motor_checkboxes)

        self._checkbox_groups = [self._tire_checkboxes, self._interior_checkboxes, self._motor_checkboxes]
        self._all_checkboxes = itertools.chain(*self._checkbox_groups)
        for checkbox in self._all_checkboxes:
            checkbox.set_selected(1)

        # configure car availability-rules
        self.car_A_rules = self._build_car_A_rules()

    def _get_tire_checkboxes(self) -> List[CheckBox]:
        tire_checkboxes:list[CheckBox] = []
        self.tire_20_inch = CheckBox(self.TIRE_20_INCH_BB)
        self.tire_22_inch = CheckBox(self.TIRE_22_INCH_BB)
        self.tire_18_inch = CheckBox(self.TIRE_18_INCH_BB)
        self.tire_19_inch = CheckBox(self.TIRE_19_INCH_BB)

        tire_checkboxes.append(self.tire_20_inch)
        tire_checkboxes.append(self.tire_22_inch)
        tire_checkboxes.append(self.tire_18_inch)
        tire_checkboxes.append(self.tire_19_inch)

        return tire_checkboxes

    def _get_interior_checkboxes(self) -> List[CheckBox]:
        interior_checkboxes = []
        self.interior_modern = CheckBox(self.INTERIOR_MODERN_BB)
        self.interior_vintage = CheckBox(self.INTERIOR_VINTAGE_BB, lambda state: print("year"))
        self.interior_SPORT = CheckBox(self.INTERIOR_SPORT_BB)

        interior_checkboxes.append(self.interior_modern)
        interior_checkboxes.append(self.interior_vintage)
        interior_checkboxes.append(self.interior_SPORT)

        return interior_checkboxes


    def _get_motor_checkboxes(self) -> List[CheckBox]:
        motor_checkboxes = []

        self.combustion_A = CheckBox(self.COMBUSTION_ENGINE_A_BB)
        self.combustion_B = CheckBox(self.COMBUSTION_ENGINE_B_BB)
        self.combustion_C = CheckBox(self.COMBUSTION_ENGINE_C_BB)
        self.electric_A = CheckBox(self.ELECTRIC_MOTOR_A_BB)
        self.electric_B = CheckBox(self.ELECTRIC_MOTOR_B_BB)

        motor_checkboxes.append(self.combustion_A)
        motor_checkboxes.append(self.combustion_B)
        motor_checkboxes.append(self.combustion_C)
        motor_checkboxes.append(self.electric_A)
        motor_checkboxes.append(self.electric_B)

        return motor_checkboxes

    def _build_car_A_rules(self):
        car_A_rules = []
        car_A_rules.append([self.tire_20_inch, self.tire_22_inch])

        return car_A_rules
        
    def _check_if_car_disabled(self, last_state):
        #TODO
        print("TODO: implement check if car disabled")
        pass


    def handle_click(self, click_position: np.ndarray = None):
        #TODO: this is duplicated code, use for each
        for checkbox_group in self._checkbox_groups:
            if get_group_bounding_box(checkbox_group).is_point_inside(click_position):
                current_state = [checkbox.is_selected() for checkbox in self._all_checkboxes]
                for checkbox in checkbox_group:
                    is_any_clicked = False
                    if checkbox.is_clicked_by(click_position):
                        #TODO check if popup needs to be shown
                        checkbox.handle_click(click_position)
                        is_any_clicked = True
                        break #TODO: use break in all handle_click-iterations in project
                if is_any_clicked:
                    self._check_if_car_disabled(current_state)

    def is_popup_open(self) -> bool:
        return self.car_disabled_popup.is_open()

class CarDisabledPopup(Page):
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(87, 101, 235, 86)
    IMG_PATH = IMAGES_PATH + "car_config_car_disabled_popup.png"
    OK_BUTTON_BB = BoundingBox(147, 143, 115, 22)

    def __init__(self):
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        self.ok_button = Button(self.OK_BUTTON_BB, lambda: self.close())

    def handle_click(self, click_position: np.ndarray = None) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click()

    def open(self):
        self.get_state()[0] = 1

    def close(self):
        self.get_state()[0] = 0

    def is_open(self):
        return self.get_state()[0]