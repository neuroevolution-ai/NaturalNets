from enum import Enum
from faulthandler import disable
import itertools
import numpy as np

from typing import List
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.car import Car
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.interfaces import HasPopups
from naturalnets.environments.app.main_window_pages.car_configurator import CarConfigurator
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.utils import get_group_bounding_box, put_text
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.check_box import CheckBox


class CarConfiguratorSettings(Page):
    STATE_LEN = 3
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
        self._car_configurator = car_configurator

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

        # all cars are initially enabled
        self.set_car_a_enabled(True)
        self.set_car_b_enabled(True)
        self.set_car_c_enabled(True)

        # configure car availability-rules
        #self.car_A_rules = self._build_car_A_components()
        self.car_config_ddis_to_curr_checkbox_status = {
        }

    def update_car_config_ddi_state(self):
        """Sets the state of the dropdown items in the car cunfigurator page according to
        the state of the checkboxes in this settings page.
        """
        self._car_configurator.set_ddi_state_from_settings({
            self._car_configurator.tire_18_ddi: self.tire_18_inch.is_selected(),
            self._car_configurator.tire_19_ddi: self.tire_19_inch.is_selected(),
            self._car_configurator.tire_20_ddi: self.tire_20_inch.is_selected(),
            self._car_configurator.tire_22_ddi: self.tire_22_inch.is_selected(),

            self._car_configurator.interior_modern_ddi: self.interior_modern.is_selected(),
            self._car_configurator.interior_vintage_ddi: self.interior_vintage.is_selected(),
            self._car_configurator.interior_sport_ddi: self.interior_sport.is_selected(),

            self._car_configurator.prop_combustion_A_ddi: self.combustion_A.is_selected(),
            self._car_configurator.prop_combustion_B_ddi: self.combustion_B.is_selected(),
            self._car_configurator.prop_combustion_C_ddi: self.combustion_C.is_selected(),
            self._car_configurator.prop_electric_A_ddi: self.electric_A.is_selected(),
            self._car_configurator.prop_electric_B_ddi: self.electric_B.is_selected(),
        })



    def set_car_a_enabled(self, enabled:bool) -> None:
        self.get_state()[0] = enabled
        self._car_configurator.car_dropdown.set_visible(self._car_configurator.car_a_ddi, enabled)

    def set_car_b_enabled(self, enabled:bool) -> None:
        self.get_state()[1] = enabled
        self._car_configurator.car_dropdown.set_visible(self._car_configurator.car_b_ddi, enabled)

    def set_car_c_enabled(self, enabled:bool) -> None:
        self.get_state()[2] = enabled
        self._car_configurator.car_dropdown.set_visible(self._car_configurator.car_c_ddi, enabled)

    def is_car_a_enabled(self) -> bool:
        return self.get_state()[0]

    def is_car_b_enabled(self) -> bool:
        return self.get_state()[1]

    def is_car_c_enabled(self) -> bool:
        return self.get_state()[2]

    def _get_tire_checkboxes(self) -> List[CheckBox]:
        tire_checkboxes:list[CheckBox] = []
        self.tire_20_inch = CheckBox(self.TIRE_20_INCH_BB, lambda is_checked: self._car_configurator.tire_dropdown.set_visible(self._car_configurator.tire_20_ddi, is_checked))
        self.tire_22_inch = CheckBox(self.TIRE_22_INCH_BB, lambda is_checked: self._car_configurator.tire_dropdown.set_visible(self._car_configurator.tire_22_ddi, is_checked))
        self.tire_18_inch = CheckBox(self.TIRE_18_INCH_BB, lambda is_checked: self._car_configurator.tire_dropdown.set_visible(self._car_configurator.tire_18_ddi, is_checked))
        self.tire_19_inch = CheckBox(self.TIRE_19_INCH_BB, lambda is_checked: self._car_configurator.tire_dropdown.set_visible(self._car_configurator.tire_19_ddi, is_checked))

        tire_checkboxes.append(self.tire_20_inch)
        tire_checkboxes.append(self.tire_22_inch)
        tire_checkboxes.append(self.tire_18_inch)
        tire_checkboxes.append(self.tire_19_inch)

        return tire_checkboxes

    def _get_interior_checkboxes(self) -> List[CheckBox]:
        interior_checkboxes = []
        self.interior_modern = CheckBox(self.INTERIOR_MODERN_BB, lambda is_checked: self._car_configurator.interior_dropdown.set_visible(self._car_configurator.interior_modern_ddi, is_checked))
        self.interior_vintage = CheckBox(self.INTERIOR_VINTAGE_BB, lambda is_checked: self._car_configurator.interior_dropdown.set_visible(self._car_configurator.interior_vintage_ddi, is_checked))
        self.interior_sport = CheckBox(self.INTERIOR_SPORT_BB, lambda is_checked: self._car_configurator.interior_dropdown.set_visible(self._car_configurator.interior_sport_ddi, is_checked))

        interior_checkboxes.append(self.interior_modern)
        interior_checkboxes.append(self.interior_vintage)
        interior_checkboxes.append(self.interior_sport)

        return interior_checkboxes


    def _get_motor_checkboxes(self) -> List[CheckBox]:
        motor_checkboxes = []

        self.combustion_A = CheckBox(self.COMBUSTION_ENGINE_A_BB, lambda is_checked: self._car_configurator.prop_dropdown.set_visible(self._car_configurator.prop_combustion_A_ddi, is_checked))
        self.combustion_B = CheckBox(self.COMBUSTION_ENGINE_B_BB, lambda is_checked: self._car_configurator.prop_dropdown.set_visible(self._car_configurator.prop_combustion_B_ddi, is_checked))
        self.combustion_C = CheckBox(self.COMBUSTION_ENGINE_C_BB, lambda is_checked: self._car_configurator.prop_dropdown.set_visible(self._car_configurator.prop_combustion_C_ddi, is_checked))
        self.electric_A = CheckBox(self.ELECTRIC_MOTOR_A_BB, lambda is_checked: self._car_configurator.prop_dropdown.set_visible(self._car_configurator.prop_electric_A_ddi, is_checked))
        self.electric_B = CheckBox(self.ELECTRIC_MOTOR_B_BB, lambda is_checked: self._car_configurator.prop_dropdown.set_visible(self._car_configurator.prop_electric_B_ddi, is_checked))

        motor_checkboxes.append(self.combustion_A)
        motor_checkboxes.append(self.combustion_B)
        motor_checkboxes.append(self.combustion_C)
        motor_checkboxes.append(self.electric_A)
        motor_checkboxes.append(self.electric_B)

        return motor_checkboxes

    def _get_disabled_cars_by_tire(self):
        car_b_disabled = [not checkbox.is_selected() for checkbox in [self.tire_18_inch, self.tire_19_inch, self.tire_20_inch]]
        pass
        
    def _check_if_car_disabled(self, last_state):
        #TODO
        #print("TODO: implement check if car disabled")
        pass


    def handle_click(self, click_position: np.ndarray):
        if self.is_popup_open():
            self.car_disabled_popup.handle_click(click_position)
        else:
            for checkbox_group in self._checkbox_groups:
                if get_group_bounding_box(checkbox_group).is_point_inside(click_position):
                    #current_state = [checkbox.is_selected() for checkbox in self._all_checkboxes]
                    for checkbox in checkbox_group:
                        #is_any_clicked = False
                        if checkbox.is_clicked_by(click_position):
                            #TODO check if popup needs to be shown
                            checkbox.handle_click(click_position)
                            #is_any_clicked = True
                            self.update_cars_enabled_status()
                            self.update_car_config_ddi_state()
                            self._car_configurator.reset()
                            break #TODO: use break in all handle_click-iterations in project
                #if is_any_clicked:
                #    self._check_if_car_disabled(current_state)

    def is_popup_open(self) -> bool:
        return self.car_disabled_popup.is_open()

    def update_cars_enabled_status(self):
        disabled_cars = []

        car_a_disabled_tire, car_b_disabled_tire, car_c_disabled_tire = self.update_cars_by_tire()
        car_a_disabled_interior, car_b_disabled_interior, car_c_disabled_interior = self.update_cars_by_interior()
        car_a_disabled_propulsion, car_b_disabled_propulsion, car_c_disabled_propulsion = self.update_cars_by_propulsion_system()

        if not car_a_disabled_tire and not car_a_disabled_interior and not car_a_disabled_propulsion:
            self.set_car_a_enabled(True)
        else:
            if self.is_car_a_enabled():
                disabled_cars.append(Car.A)
            self.set_car_a_enabled(False)

        if not car_b_disabled_tire and not car_b_disabled_interior and not car_b_disabled_propulsion:
            self.set_car_b_enabled(True)
        else:
            if self.is_car_b_enabled():
                disabled_cars.append(Car.B)
            self.set_car_b_enabled(False)

        if not car_c_disabled_tire and not car_c_disabled_interior and not car_c_disabled_propulsion:
            self.set_car_c_enabled(True)
        else:
            if self.is_car_c_enabled():
                disabled_cars.append(Car.C)
            self.set_car_c_enabled(False)

        if len(disabled_cars) > 0:
            self.car_disabled_popup.open(disabled_cars)

    def update_cars_by_tire(self):
        car_a_disabled = True
        car_b_disabled = True
        car_c_disabled = True

        if self.tire_18_inch.is_selected():
            car_b_disabled = False
        if self.tire_19_inch.is_selected():
            car_b_disabled = False
            car_c_disabled = False
        if self.tire_20_inch.is_selected():
            car_a_disabled = False
            car_b_disabled = False
            car_c_disabled = False
        if self.tire_22_inch.is_selected():
            car_a_disabled = False
            car_c_disabled = False

        return car_a_disabled, car_b_disabled, car_c_disabled

    def update_cars_by_interior(self):
        car_a_disabled = True
        car_b_disabled = True
        car_c_disabled = True

        if self.interior_modern.is_selected():
            car_a_disabled = False
            car_b_disabled = False
        if self.interior_vintage.is_selected():
            car_a_disabled = False
            car_c_disabled = False
        if self.interior_sport.is_selected():
            car_b_disabled = False
            car_c_disabled = False

        return car_a_disabled, car_b_disabled, car_c_disabled

    def update_cars_by_propulsion_system(self):
        car_a_disabled = True
        car_b_disabled = True
        car_c_disabled = True

        if self.combustion_A.is_selected():
            car_a_disabled = False
        if self.combustion_B.is_selected():
            car_c_disabled = False
        if self.combustion_C.is_selected():
            car_a_disabled = False
            car_c_disabled = False
        if self.electric_A.is_selected():
            car_b_disabled = False
            car_c_disabled = False
        if self.electric_B.is_selected():
            car_b_disabled = False
            car_c_disabled = False

        return car_a_disabled, car_b_disabled, car_c_disabled

    def render(self, img: np.ndarray):
        img = super().render(img)
        if self.is_popup_open():
            img = self.car_disabled_popup.render(img)
        return img


class CarDisabledPopup(Page):
    STATE_LEN = 4 # state-index 0 for open/closed state, rest for shown "text" 
                  # (which cars were disabled by last click)
    BOUNDING_BOX = BoundingBox(87, 101, 235, 86)
    IMG_PATH = IMAGES_PATH + "car_config_car_disabled_popup.png"
    OK_BUTTON_BB = BoundingBox(147, 143, 115, 22)

    def __init__(self):
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        self.ok_button = Button(self.OK_BUTTON_BB, lambda: self.close())
        self.index_to_car_str = {1: "Car A", 2: "Car B", 3: "Car C"}


    def _get_disabled_cars_str(self) -> List[str]:
        disabled_cars = "Disabled "
        for i in range(1,4):
            if self.get_state()[i] == 1:
                disabled_cars += self.index_to_car_str[i] + " "
        return disabled_cars



    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click()

    def open(self, disabled_cars:List[str]):
        if Car.A in disabled_cars:
            self.get_state()[Car.A.value] = 1
        if Car.B in disabled_cars:
            self.get_state()[Car.B.value] = 1
        if Car.C in disabled_cars:
            self.get_state()[Car.C.value] = 1

        self.get_state()[0] = 1 # open-state

    def close(self):
        self.get_state()[1:self.STATE_LEN] = np.zeros(self.STATE_LEN - 1, dtype=int)
        self.get_state()[0] = 0 # open-state

    def is_open(self):
        return self.get_state()[0]

    def render(self, img: np.ndarray):
        img = super().render(img)
        bottomLeftCorner = (107, 135) # global position of text
        put_text(img, self._get_disabled_cars_str(), bottomLeftCorner, 0.4)
        return img
        