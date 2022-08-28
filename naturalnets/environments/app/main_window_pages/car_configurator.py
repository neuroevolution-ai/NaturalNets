import os
from typing import Dict

import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.enums import Car
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.utils import put_text, render_onto_bb
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem


class CarConfigurator(Page):
    """The car-configurator page in the main-window.

       State description:
            state[i]: denotes if a value has been selected in the i-th dropdown, i.e.
            the dropdown was opened and a value clicked after the last reset of that
            dropdown. Dropdowns are reset when the car configuration is shown or when
            a previous dropdown's value is selected.
    """

    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "car_configurator.png")

    CAR_DROPDOWN_BB = BoundingBox(252, 108, 166, 22)
    TIRE_DROPDOWN_BB = BoundingBox(252, 189, 166, 22)
    INTERIOR_DROPDOWN_BB = BoundingBox(252, 270, 166, 22)
    PROPULSION_DROPDOWN_BB = BoundingBox(252, 351, 166, 22)

    TIRE_FRAME_BB = BoundingBox(125, 163, 303, 75)
    TIRE_FRAME_IMG_PATH = os.path.join(IMAGES_PATH, "car_config_tire_frame.png")

    INTERIOR_FRAME_BB = BoundingBox(125, 244, 303, 75)
    INTERIOR_FRAME_IMG_PATH = os.path.join(IMAGES_PATH, "car_config_interior_frame.png")

    PROP_FRAME_BB = BoundingBox(125, 325, 303, 75)
    PROP_FRAME_IMG_PATH = os.path.join(IMAGES_PATH, "car_config_prop_frame.png")

    BUTTON_BB = BoundingBox(125, 406, 303, 22)
    BUTTON_IMG_PATH = os.path.join(IMAGES_PATH, "car_config_button_frame.png")

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
        self.ddi_state_from_settings: Dict[DropdownItem, int] = {}

        # Add show configuration button and window
        self.popup = CarConfiguratorPopup(self)
        self.add_child(self.popup)
        self.show_config_button = Button(self.BUTTON_BB, self.popup.open)

    def get_opened_dropdown_index(self) -> int:
        for index, dropdown in enumerate(self.dropdowns):
            if dropdown.is_open():
                return index
        return None

    def handle_click(self, click_position: np.ndarray):
        dropdown_value_clicked = False

        if self.is_popup_open():
            self.popup.handle_click(click_position)
            return

        opened_dd_index = self.get_opened_dropdown_index()
        if opened_dd_index is not None:
            dropdown = self.dropdowns[opened_dd_index]
            if dropdown.is_clicked_by(click_position):
                dropdown_value_clicked = True
            dropdown.handle_click(click_position)
            if dropdown_value_clicked:
                self._update_dropdowns_on_dropdown_value_click(opened_dd_index)
            return

        # Show config button only clickable if a value has been selected in the last dropdown
        if (self.get_state()[len(self.dropdowns) - 1] != 0
                and self.show_config_button.is_clicked_by(click_position)):
            self.show_config_button.handle_click(click_position)
            return

        # handle dropdown-click if dropdown is shown (a value was selected in a previous dropdown)
        for index, dropdown in enumerate(self.dropdowns):
            if dropdown.is_clicked_by(click_position):
                if index == 0 or self._is_dropdown_value_selected(index - 1):
                    if dropdown.is_open():
                        dropdown_value_clicked = True
                    dropdown.handle_click(click_position)
                    if dropdown_value_clicked:
                        self._update_dropdowns_on_dropdown_value_click(index)
                    return

    def _update_dropdowns_on_dropdown_value_click(self, index: int) -> None:
        """Updates all dropdowns (sets visibility and/or initial selected item) when a dropdown
        value is clicked (i.e. dropdown.is_open() and dropdown.is_clicked_by(click_position))."""
        dropdown = self.dropdowns[index]
        # adjust shown dropdowns when a dropdown value is clicked
        self.get_state()[index] = 1 # set dropdown-value selected to true
        if index == 0:  # car dropdown
            self._adjust_visible_dropdown_items_by_car(dropdown.get_current_value())
        # reset to dropdown if next dropdown(s) already have selected values
        if (index + 1 < len(self.dropdowns)
                and self._is_dropdown_value_selected(index + 1)):
            self._reset_to(index)

    def _is_dropdown_value_selected(self, index: int) -> int:
        if index < 0:
            return 0
        return self.get_state()[index]


    def set_ddi_state_from_settings(self, ddi_state: Dict[DropdownItem, int]) -> None:
        """Used by the car-configurator-settings page to set which checkboxes are currently enabled
        in the settings.

        Args:
            ddi_state (Dict[DropdownItem, int]): Mapping from car-config dropdown items
            to enabled status.
        """
        self.ddi_state_from_settings = ddi_state

    def _adjust_visible_dropdown_items_by_car(self, car: Car) -> None:
        self.reset_ddi_visibility_to_settings_state()

        if car is None:
            return
        if car == Car.A:
            self.tire_18_ddi.set_visible(0)
            self.tire_19_ddi.set_visible(0)

            self.interior_sport_ddi.set_visible(0)

            self.prop_combustion_b_ddi.set_visible(0)
            self.prop_electric_a_ddi.set_visible(0)
            self.prop_electric_b_ddi.set_visible(0)
        elif car == Car.B:
            self.tire_22_ddi.set_visible(0)

            self.interior_vintage_ddi.set_visible(0)

            self.prop_combustion_a_ddi.set_visible(0)
            self.prop_combustion_b_ddi.set_visible(0)
            self.prop_combustion_c_ddi.set_visible(0)
        elif car == Car.C:
            self.tire_18_ddi.set_visible(0)

            self.interior_modern_ddi.set_visible(0)

            self.prop_combustion_a_ddi.set_visible(0)

        self._select_initial_dropdown_items(1)

    def reset_ddi_visibility_to_settings_state(self):
        """Resets all dropdown items visibility state to the visibility state specified
        in the car-configurator settings."""
        for ddi, is_visible in self.ddi_state_from_settings.items():
            ddi.set_visible(is_visible)

    def reset(self):
        """Resets all dropdowns/hides all dropdowns but the first."""
        for i in range(len(self.dropdowns)):
            self.get_state()[i] = 0

        self.reset_ddi_visibility_to_settings_state()
        self._select_initial_dropdown_items(0)

    def _reset_to(self, dd_index: int):
        """Resets all dropdowns selection up to self.dropdowns[dd_index].
        """
        for i in range(dd_index + 1, len(self.dropdowns)):
            self.get_state()[i] = 0
        self._select_initial_dropdown_items(dd_index + 1)

    def _select_initial_dropdown_items(self, index: int) -> None:
        """Sets the initial dropdown items (first visible item in dropdown) for all dropdowns
        from the given index to the last dropdown."""
        for i in range(index, len(self.dropdowns)):
            dropdown = self.dropdowns[i]
            visible_items = dropdown.get_visible_items()
            if len(visible_items) == 0:
                dropdown.set_selected_item(None)
                return
            for item in dropdown.get_visible_items():
                dropdown.set_selected_item(item)
                break

    def is_dropdown_open(self) -> int:
        return (self.car_dropdown.is_open()
                or self.tire_dropdown.is_open()
                or self.interior_dropdown.is_open()
                or self.prop_dropdown.is_open())

    def is_popup_open(self) -> int:
        return self.popup.is_open()

    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)

        if self.get_state()[0]:
            frame = cv2.imread(self.TIRE_FRAME_IMG_PATH)
            render_onto_bb(img, self.TIRE_FRAME_BB, frame)

        if self.get_state()[1]:
            frame = cv2.imread(self.INTERIOR_FRAME_IMG_PATH)
            render_onto_bb(img, self.INTERIOR_FRAME_BB, frame)

        if self.get_state()[2]:
            frame = cv2.imread(self.PROP_FRAME_IMG_PATH)
            render_onto_bb(img, self.PROP_FRAME_BB, frame)

        if self.get_state()[3]:
            frame = cv2.imread(self.BUTTON_IMG_PATH)
            render_onto_bb(img, self.BUTTON_BB, frame)

        # only render dropdowns if the previous dropdown value was selected
        # (replaces widget rendering, since all widgets of the car configurator
        # are dropdowns)
        for index, dropdown in enumerate(self.dropdowns):
            if index == 0:
                img = dropdown.render(img)
            elif self._is_dropdown_value_selected(index - 1):
                img = dropdown.render(img)

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
    IMG_PATH = os.path.join(IMAGES_PATH, "car_config_popup.png")

    OK_BUTTON_BB = BoundingBox(148, 244, 152, 22)

    def __init__(self, car_configurator: CarConfigurator):
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        self.ok_button = Button(self.OK_BUTTON_BB, self.close)
        self.car_configurator = car_configurator

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def open(self) -> None:
        """Opens this popup."""
        self.get_state()[0] = 1

    def close(self) -> None:
        """Closes this popup."""
        self.get_state()[0] = 0
        self.car_configurator.reset()

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]

    def render(self, img: np.ndarray):
        img = super().render(img)
        x, y, _, height = self.CONFIGURATION_TEXT_BB.get_as_tuple()
        props = [
            f"Propulsion System: {self.car_configurator.prop_dropdown.get_current_value()}",
            f"Interior: {self.car_configurator.interior_dropdown.get_current_value()}",
            f"Tires: {self.car_configurator.tire_dropdown.get_current_value()}",
            f"Car: {self.car_configurator.car_dropdown.get_current_value()}"
        ]

        space = 16
        for i, prop in enumerate(props):
            bottom_left_corner = (x, y + height - i * space)
            put_text(img, prop, bottom_left_corner, font_scale=0.4)
        return img
