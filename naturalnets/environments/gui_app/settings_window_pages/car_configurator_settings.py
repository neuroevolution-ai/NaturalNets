import itertools
import os
from typing import List

import numpy as np


from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.enums import Car
from naturalnets.environments.gui_app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.gui_app.main_window_pages.car_configurator import CarConfigurator
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.utils import get_group_bounding_box, put_text
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox


class CarConfiguratorSettings(Page):
    """The car-configurator settings page, manipulates the car-configurator page.

       State description:
            state[i]: the enabled-state of car i, i in {0,1,2}.
    """
    STATE_LEN = 3
    IMG_PATH = os.path.join(IMAGES_PATH, "car_configurator_settings.png")

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

    def __init__(self, car_configurator: CarConfigurator):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        self._car_configurator = car_configurator

        # add popup window as child
        self.car_disabled_popup = CarDisabledPopup()
        self.add_child(self.car_disabled_popup)

        # configure checkboxes
        tire_checkboxes = self._create_tire_checkboxes()
        self.add_widgets(tire_checkboxes)

        interior_checkboxes = self._create_interior_checkboxes()
        self.add_widgets(interior_checkboxes)

        motor_checkboxes = self._create_propulsion_system_checkboxes()
        self.add_widgets(motor_checkboxes)

        self._checkbox_groups = [
            tire_checkboxes,
            interior_checkboxes,
            motor_checkboxes
        ]

        self._checkbox_group_bbs = [
            get_group_bounding_box(tire_checkboxes),
            get_group_bounding_box(interior_checkboxes),
            get_group_bounding_box(motor_checkboxes)
        ]

        # all checkboxes are initially selected
        all_checkboxes = itertools.chain(*self._checkbox_groups)
        for checkbox in all_checkboxes:
            checkbox.set_selected(1)

        # all cars are initially enabled
        self.set_car_a_enabled(1)
        self.set_car_b_enabled(1)
        self.set_car_c_enabled(1)
        self.update_car_config_ddi_state()

    def update_car_config_ddi_state(self):
        """Sets the state of the dropdown items in the car configurator page according to
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

            self._car_configurator.prop_combustion_a_ddi: self.combustion_a.is_selected(),
            self._car_configurator.prop_combustion_b_ddi: self.combustion_b.is_selected(),
            self._car_configurator.prop_combustion_c_ddi: self.combustion_c.is_selected(),
            self._car_configurator.prop_electric_a_ddi: self.electric_a.is_selected(),
            self._car_configurator.prop_electric_b_ddi: self.electric_b.is_selected(),
        })

        self._car_configurator.reset()

    def set_car_a_enabled(self, enabled: int) -> None:
        self.get_state()[0] = enabled
        self._car_configurator.car_a_ddi.set_visible(enabled)

    def set_car_b_enabled(self, enabled: int) -> None:
        self.get_state()[1] = enabled
        self._car_configurator.car_b_ddi.set_visible(enabled)

    def set_car_c_enabled(self, enabled: int) -> None:
        self.get_state()[2] = enabled
        self._car_configurator.car_c_ddi.set_visible(enabled)

    def is_car_a_enabled(self) -> int:
        return self.get_state()[0]

    def is_car_b_enabled(self) -> int:
        return self.get_state()[1]

    def is_car_c_enabled(self) -> int:
        return self.get_state()[2]

    def _create_tire_checkboxes(self) -> List[CheckBox]:
        tire_checkboxes: List[CheckBox] = []
        self.tire_20_inch = CheckBox(
            self.TIRE_20_INCH_BB,
            self._car_configurator.tire_20_ddi.set_visible
        )
        self.tire_22_inch = CheckBox(
            self.TIRE_22_INCH_BB,
            self._car_configurator.tire_22_ddi.set_visible
        )
        self.tire_18_inch = CheckBox(
            self.TIRE_18_INCH_BB,
            self._car_configurator.tire_18_ddi.set_visible
        )
        self.tire_19_inch = CheckBox(
            self.TIRE_19_INCH_BB,
            self._car_configurator.tire_19_ddi.set_visible
        )

        tire_checkboxes.append(self.tire_20_inch)
        tire_checkboxes.append(self.tire_22_inch)
        tire_checkboxes.append(self.tire_18_inch)
        tire_checkboxes.append(self.tire_19_inch)

        return tire_checkboxes

    def _create_interior_checkboxes(self) -> List[CheckBox]:
        interior_checkboxes = []
        self.interior_modern = CheckBox(
            self.INTERIOR_MODERN_BB,
            self._car_configurator.interior_modern_ddi.set_visible
        )
        self.interior_vintage = CheckBox(
            self.INTERIOR_VINTAGE_BB,
            self._car_configurator.interior_vintage_ddi.set_visible
        )
        self.interior_sport = CheckBox(
            self.INTERIOR_SPORT_BB,
            self._car_configurator.interior_sport_ddi.set_visible
        )

        interior_checkboxes.append(self.interior_modern)
        interior_checkboxes.append(self.interior_vintage)
        interior_checkboxes.append(self.interior_sport)

        return interior_checkboxes

    def _create_propulsion_system_checkboxes(self) -> List[CheckBox]:
        motor_checkboxes = []

        self.combustion_a = CheckBox(
            self.COMBUSTION_ENGINE_A_BB,
            self._car_configurator.prop_combustion_a_ddi.set_visible
        )
        self.combustion_b = CheckBox(
            self.COMBUSTION_ENGINE_B_BB,
            self._car_configurator.prop_combustion_b_ddi.set_visible
        )
        self.combustion_c = CheckBox(
            self.COMBUSTION_ENGINE_C_BB,
            self._car_configurator.prop_combustion_c_ddi.set_visible
        )
        self.electric_a = CheckBox(
            self.ELECTRIC_MOTOR_A_BB,
            self._car_configurator.prop_electric_a_ddi.set_visible
        )
        self.electric_b = CheckBox(
            self.ELECTRIC_MOTOR_B_BB,
            self._car_configurator.prop_electric_b_ddi.set_visible
        )

        motor_checkboxes.append(self.combustion_a)
        motor_checkboxes.append(self.combustion_b)
        motor_checkboxes.append(self.combustion_c)
        motor_checkboxes.append(self.electric_a)
        motor_checkboxes.append(self.electric_b)

        return motor_checkboxes

    def handle_click(self, click_position: np.ndarray):
        if self.is_popup_open():
            self.car_disabled_popup.handle_click(click_position)
            return
        for i, checkbox_group in enumerate(self._checkbox_groups):
            if self._checkbox_group_bbs[i].is_point_inside(click_position):
                for checkbox in checkbox_group:
                    if checkbox.is_clicked_by(click_position):
                        checkbox.handle_click(click_position)
                        self.update_cars_enabled_status()
                        self.update_car_config_ddi_state()
                        self._car_configurator.reset()
                        break

    def is_popup_open(self) -> int:
        return self.car_disabled_popup.is_open()

    # Pretty much copied from the masters-thesis code this app is based on.
    def update_cars_enabled_status(self):
        """Updates the enabled cars, by changing the state that is assigned to the respective setting."""
        disabled_cars = []

        car_a_disabled_tire, car_b_disabled_tire, car_c_disabled_tire = self.update_cars_by_tire()
        car_a_disabled_interior, car_b_disabled_interior, car_c_disabled_interior = self.update_cars_by_interior()
        disabled_propulsion = self.update_cars_by_propulsion_system()
        car_a_disabled_propulsion, car_b_disabled_propulsion, car_c_disabled_propulsion = disabled_propulsion

        if (not car_a_disabled_tire
                and not car_a_disabled_interior
                and not car_a_disabled_propulsion):
            self.set_car_a_enabled(1)
        else:
            if self.is_car_a_enabled():
                disabled_cars.append(Car.A)
            self.set_car_a_enabled(0)

        if (not car_b_disabled_tire
                and not car_b_disabled_interior
                and not car_b_disabled_propulsion):
            self.set_car_b_enabled(1)
        else:
            if self.is_car_b_enabled():
                disabled_cars.append(Car.B)
            self.set_car_b_enabled(0)

        if (not car_c_disabled_tire
                and not car_c_disabled_interior
                and not car_c_disabled_propulsion):
            self.set_car_c_enabled(1)
        else:
            if self.is_car_c_enabled():
                disabled_cars.append(Car.C)
            self.set_car_c_enabled(0)

        if len(disabled_cars) > 0:
            self.car_disabled_popup.open(disabled_cars)

    # Pretty much copied from the masters-thesis code this app is based on.
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

    # pretty much copied from the masters-thesis code this app is based on.
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

    # pretty much copied from the masters-thesis code this app is based on.
    def update_cars_by_propulsion_system(self):
        car_a_disabled = True
        car_b_disabled = True
        car_c_disabled = True

        if self.combustion_a.is_selected():
            car_a_disabled = False
        if self.combustion_b.is_selected():
            car_c_disabled = False
        if self.combustion_c.is_selected():
            car_a_disabled = False
            car_c_disabled = False
        if self.electric_a.is_selected():
            car_b_disabled = False
            car_c_disabled = False
        if self.electric_b.is_selected():
            car_b_disabled = False
            car_c_disabled = False

        return car_a_disabled, car_b_disabled, car_c_disabled

    def render(self, img: np.ndarray):
        """Renders the car-configurator settings as well as its popup 
        (if opened) onto the given image."""
        img = super().render(img)
        if self.is_popup_open():
            img = self.car_disabled_popup.render(img)
        return img


class CarDisabledPopup(Page):
    """Popup for the car-configurator settings (pops up when a car is disabled through the
    click of a checkbox).

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(87, 101, 235, 86)
    IMG_PATH = os.path.join(IMAGES_PATH, "car_config_car_disabled_popup.png")
    OK_BUTTON_BB = BoundingBox(147, 143, 115, 22)

    def __init__(self):
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        self.ok_button = Button(self.OK_BUTTON_BB, self.close)
        self.disabled_cars: List[str] = []

    def _get_disabled_cars_str(self) -> str:
        disabled_cars_str = "Disabled "
        for car in self.disabled_cars:
            disabled_cars_str += car + " "
        return disabled_cars_str

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def open(self, disabled_cars: List[Car]):
        """Opens this popup and adds the disabled cars to the list of cars to be
        shown in this popup."""
        if Car.A in disabled_cars:
            self.disabled_cars.append("Car A")
        if Car.B in disabled_cars:
            self.disabled_cars.append("Car B")
        if Car.C in disabled_cars:
            self.disabled_cars.append("Car C")

        self.get_state()[0] = 1  # open-state

    def close(self):
        """Closes this popup and empties its list of disabled cars."""
        self.disabled_cars = []
        self.get_state()[0] = 0  # open-state

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]

    def render(self, img: np.ndarray):
        img = super().render(img)
        bottom_left_corner = (107, 135)  # global position of text
        put_text(img, self._get_disabled_cars_str(), bottom_left_corner, 0.4)
        return img
