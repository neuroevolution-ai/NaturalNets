from typing import Dict
import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.enums import Car
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.utils import put_text, render_onto_bb
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem

class CarConfigurator(Page):
    """The car-configurator page in the main-window.
    """

    STATE_LEN = 0
    IMG_PATH = IMAGES_PATH + "car_configurator.png"

    CAR_DROPDOWN_BB = BoundingBox(252, 108, 166, 22)
    TIRE_DROPDOWN_BB = BoundingBox(252, 189, 166, 22)
    INTERIOR_DROPDOWN_BB = BoundingBox(252, 270, 166, 22)
    PROPULSION_DROPDOWN_BB = BoundingBox(252, 351, 166, 22)

    TIRE_FRAME_BB = BoundingBox(125, 163, 303, 75)
    TIRE_FRAME_IMG_PATH = IMAGES_PATH + "car_config_tire_frame.png"

    INTERIOR_FRAME_BB = BoundingBox(125, 244, 303, 75)
    INTERIOR_FRAME_IMG_PATH = IMAGES_PATH + "car_config_interior_frame.png"

    PROP_FRAME_BB = BoundingBox(125, 325, 303, 75)
    PROP_FRAME_IMG_PATH = IMAGES_PATH + "car_config_prop_frame.png"

    BUTTON_BB = BoundingBox(125, 406, 303, 22)
    BUTTON_IMG_PATH = IMAGES_PATH + "car_config_button_frame.png"

    def __init__(self):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        # add car dropdown
        self.car_a_ddi = DropdownItem(Car.A, display_name="Car A")
        self.car_b_ddi = DropdownItem(Car.B, display_name="Car B")
        self.car_c_ddi = DropdownItem(Car.C, display_name="Car C")
        self.car_dropdown = Dropdown(self.CAR_DROPDOWN_BB, [self.car_a_ddi,
                                                            self.car_b_ddi,
                                                            self.car_c_ddi])
        self.add_widget(self.car_dropdown)

        # add tire dropdown
        self.tire_20_ddi = DropdownItem("Tire 20", "Tire 20")
        self.tire_22_ddi = DropdownItem("Tire 22", "Tire 22")
        self.tire_18_ddi = DropdownItem("Tire 18", "Tire 18")
        self.tire_19_ddi = DropdownItem("Tire 19", "Tire 19")
        self.tire_dropdown = Dropdown(self.TIRE_DROPDOWN_BB, [self.tire_18_ddi,
                                                              self.tire_19_ddi,
                                                              self.tire_20_ddi,
                                                              self.tire_22_ddi])
        self.add_widget(self.tire_dropdown)

        # add interior dropdown
        self.interior_modern_ddi = DropdownItem("Modern", "Modern")
        self.interior_vintage_ddi = DropdownItem("Vintage", "Vintage")
        self.interior_sport_ddi = DropdownItem("Sport", "Sport")
        self.interior_dropdown = Dropdown(self.INTERIOR_DROPDOWN_BB, [self.interior_modern_ddi,
                                                                      self.interior_vintage_ddi,
                                                                      self.interior_sport_ddi])
        self.add_widget(self.interior_dropdown)

        # add propulsion system dropdown
        self.prop_combustion_a_ddi = DropdownItem("Combustion A", "Combustion A")
        self.prop_combustion_b_ddi = DropdownItem("Combustion B", "Combustion B")
        self.prop_combustion_c_ddi = DropdownItem("Combustion C", "Combustion C")
        self.prop_electric_a_ddi = DropdownItem("Electric A", "Electric A")
        self.prop_electric_b_ddi = DropdownItem("Electric B", "Electric B")
        self.prop_dropdown = Dropdown(self.PROPULSION_DROPDOWN_BB, [self.prop_combustion_a_ddi,
                                                                    self.prop_combustion_b_ddi,
                                                                    self.prop_combustion_c_ddi,
                                                                    self.prop_electric_a_ddi,
                                                                    self.prop_electric_b_ddi])
        self.add_widget(self.prop_dropdown)

        # setup data structures
        self.dropdowns = [self.car_dropdown,
                          self.tire_dropdown,
                          self.interior_dropdown,
                          self.prop_dropdown]
        self.ddi_state_from_settings:dict[DropdownItem, bool] = {}

        #add show configuration button and window
        self.popup = CarConfiguratorPopup(self)
        self.show_config_button = Button(self.BUTTON_BB, self.popup.open)


    def handle_click(self, click_position: np.ndarray):
        if self.is_popup_open():
            self.popup.handle_click(click_position)
            return

        # button only clickable if a value is selected in last dropdown
        if self.dropdowns[len(self.dropdowns) - 1].get_current_value() is not None\
                and self.show_config_button.is_clicked_by(click_position):
            self.show_config_button.handle_click()
            return

        for index, dropdown in enumerate(self.dropdowns):
            if dropdown.is_clicked_by(click_position) or dropdown.is_open():
                old_value = dropdown.get_current_value()
                if index == 0 or self.dropdowns[index - 1].get_selected_item() is not None:
                    dropdown.handle_click(click_position)

                # check if the click changed a dropdown-value to another
                if old_value is not dropdown.get_current_value():
                    if index == 0: # car dropdown
                        self._adjust_visible_dropdown_items_by_car(dropdown.get_current_value())
                    # reset to dropdown if next dropdown(s) already have selected values
                    if index + 1 < len(self.dropdowns)\
                            and self.dropdowns[index + 1].get_selected_item() is not None:
                        self._reset_to(index)
                return


    def set_ddi_state_from_settings(self, ddi_state:Dict[DropdownItem, bool]) -> None:
        """Used by the car-configurator-settings page to set which checkboxes are currently enabled
        in the settings.

        Args:
            ddi_state (Dict[DropdownItem, bool]): Mapping from car-config dropdown items
            to enabled status.
        """
        self.ddi_state_from_settings = ddi_state

    def _adjust_visible_dropdown_items_by_car(self, car: Car) -> None:
        self.reset_ddi_visibility_to_stettings_state()

        if car is None:
            return
        if car == Car.A:
            self.tire_dropdown.set_visible(self.tire_18_ddi, False)
            self.tire_dropdown.set_visible(self.tire_19_ddi, False)

            self.interior_dropdown.set_visible(self.interior_sport_ddi, False)

            self.prop_dropdown.set_visible(self.prop_combustion_b_ddi, False)
            self.prop_dropdown.set_visible(self.prop_electric_a_ddi, False)
            self.prop_dropdown.set_visible(self.prop_electric_b_ddi, False)
        elif car == Car.B:
            self.tire_dropdown.set_visible(self.tire_22_ddi, False)

            self.interior_dropdown.set_visible(self.interior_vintage_ddi, False)

            self.prop_dropdown.set_visible(self.prop_combustion_a_ddi, False)
            self.prop_dropdown.set_visible(self.prop_combustion_b_ddi, False)
            self.prop_dropdown.set_visible(self.prop_combustion_c_ddi, False)
        elif car == Car.C:
            self.tire_dropdown.set_visible(self.tire_18_ddi, False)

            self.interior_dropdown.set_visible(self.interior_modern_ddi, False)

            self.prop_dropdown.set_visible(self.prop_combustion_a_ddi, False)

    def reset_ddi_visibility_to_stettings_state(self):
        """Resets all dropdown items visibility state to the visibility state specified
        in the car-configurator settings."""
        for ddi, is_visible in self.ddi_state_from_settings.items():
            ddi.set_visible(is_visible)

    def reset(self):
        """Resets all dropdowns/hides all dropdowns but the first."""
        for dropdown in self.dropdowns:
            dropdown.set_selected_item(None)

        self.reset_ddi_visibility_to_stettings_state()


    def _reset_to(self, dd_index:int):
        """Resets all dropdowns selection up to self.dropdowns[dd_index].
        """
        for i in range(dd_index + 1, len(self.dropdowns)):
            self.dropdowns[i].set_selected_item(None)


    def is_dropdown_open(self) -> bool:
        return self.car_dropdown.is_open() or self.tire_dropdown.is_open()\
                    or self.interior_dropdown.is_open()\
                    or self.prop_dropdown.is_open()

    def is_popup_open(self) -> bool:
        return self.popup.is_open()

    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)

        if self.car_dropdown.get_selected_item() is not None:
            frame = cv2.imread(self.TIRE_FRAME_IMG_PATH)
            render_onto_bb(img, self.TIRE_FRAME_BB, frame)

        if self.tire_dropdown.get_selected_item() is not None:
            frame = cv2.imread(self.INTERIOR_FRAME_IMG_PATH)
            render_onto_bb(img, self.INTERIOR_FRAME_BB, frame)

        if self.interior_dropdown.get_selected_item() is not None:
            frame = cv2.imread(self.PROP_FRAME_IMG_PATH)
            render_onto_bb(img, self.PROP_FRAME_BB, frame)

        if self.prop_dropdown.get_selected_item() is not None:
            frame = cv2.imread(self.BUTTON_IMG_PATH)
            render_onto_bb(img, self.BUTTON_BB, frame)

        for widget in self.get_widgets():
            img = widget.render(img)

        if self.is_popup_open():
            img = self.popup.render(img)

        return img

class CarConfiguratorPopup(Page):
    """Popup for the car-configurator (pops up when the "show configuration"-button is clicked).

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(75, 160, 298, 128)
    CONFIGURATION_TEXT_BB = BoundingBox(94, 167, 263, 73)
    IMG_PATH = IMAGES_PATH + "car_config_popup.png"

    OK_BUTTON_BB = BoundingBox(148, 244, 152, 22)

    def __init__(self, car_configurator:CarConfigurator):
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        self.ok_button = Button(self.OK_BUTTON_BB, self.close)
        self.car_configurator = car_configurator

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click()

    def open(self) -> None:
        """Opens this popup."""
        self.get_state()[0] = 1

    def close(self) -> None:
        """Closes this popup."""
        self.get_state()[0] = 0
        self.car_configurator.reset()

    def is_open(self) -> bool:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]

    def render(self, img: np.ndarray):
        img = super().render(img)
        x, y, _, height = self.CONFIGURATION_TEXT_BB.get_as_tuple()
        props = [f"Propulsion System: {self.car_configurator.prop_dropdown.get_current_value()}",
            f"Interior: {self.car_configurator.interior_dropdown.get_current_value()}",
            f"Tires: {self.car_configurator.tire_dropdown.get_current_value()}",
            f"Car: {self.car_configurator.car_dropdown.get_current_value()}"]

        space = 16
        for i, prop in enumerate(props):
            bottom_left_corner = (x, y + height - i*space)
            put_text(img, prop, bottom_left_corner, 0.4)
        return img
