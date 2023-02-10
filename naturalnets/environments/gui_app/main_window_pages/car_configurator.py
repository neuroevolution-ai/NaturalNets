import os
from typing import Dict, List, Tuple

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.gui_app.enums import Car, TireSize, Interior, PropulsionSystem
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem


class CarConfigurator(Page, RewardElement):
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
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        # Car Dropdowns
        self.car_a_ddi = DropdownItem(Car.A, display_name="Car A")
        self.car_b_ddi = DropdownItem(Car.B, display_name="Car B")
        self.car_c_ddi = DropdownItem(Car.C, display_name="Car C")
        self.car_dropdown = Dropdown(self.CAR_DROPDOWN_BB, [self.car_a_ddi,
                                                            self.car_b_ddi,
                                                            self.car_c_ddi])
        self.add_widget(self.car_dropdown)

        # Tire Dropdowns
        self.tire_20_ddi = DropdownItem(TireSize.TIRE_20, str(TireSize.TIRE_20.value))
        self.tire_22_ddi = DropdownItem(TireSize.TIRE_22, str(TireSize.TIRE_22.value))
        self.tire_18_ddi = DropdownItem(TireSize.TIRE_18, str(TireSize.TIRE_18.value))
        self.tire_19_ddi = DropdownItem(TireSize.TIRE_19, str(TireSize.TIRE_19.value))
        self.tire_dropdown = Dropdown(self.TIRE_DROPDOWN_BB, [self.tire_18_ddi,
                                                              self.tire_19_ddi,
                                                              self.tire_20_ddi,
                                                              self.tire_22_ddi])
        self.add_widget(self.tire_dropdown)

        # Interior Dropdowns
        self.interior_modern_ddi = DropdownItem(Interior.MODERN, str(Interior.MODERN.value))
        self.interior_vintage_ddi = DropdownItem(Interior.VINTAGE, str(Interior.VINTAGE.value))
        self.interior_sport_ddi = DropdownItem(Interior.SPORT, str(Interior.SPORT.value))
        self.interior_dropdown = Dropdown(self.INTERIOR_DROPDOWN_BB, [self.interior_modern_ddi,
                                                                      self.interior_vintage_ddi,
                                                                      self.interior_sport_ddi])
        self.add_widget(self.interior_dropdown)

        # Propulsion System Dropdowns
        self.prop_combustion_a_ddi = DropdownItem(
            PropulsionSystem.COMBUSTION_ENGINE_A,
            str(PropulsionSystem.COMBUSTION_ENGINE_A.value)
        )
        self.prop_combustion_b_ddi = DropdownItem(
            PropulsionSystem.COMBUSTION_ENGINE_B,
            str(PropulsionSystem.COMBUSTION_ENGINE_B.value)
        )
        self.prop_combustion_c_ddi = DropdownItem(
            PropulsionSystem.COMBUSTION_ENGINE_C,
            str(PropulsionSystem.COMBUSTION_ENGINE_C.value)
        )
        self.prop_electric_a_ddi = DropdownItem(
            PropulsionSystem.ELECTRIC_MOTOR_A,
            str(PropulsionSystem.ELECTRIC_MOTOR_A.value)
        )
        self.prop_electric_b_ddi = DropdownItem(
            PropulsionSystem.ELECTRIC_MOTOR_B,
            str(PropulsionSystem.ELECTRIC_MOTOR_B.value)
        )
        self.prop_dropdown = Dropdown(self.PROPULSION_DROPDOWN_BB, [self.prop_combustion_a_ddi,
                                                                    self.prop_combustion_b_ddi,
                                                                    self.prop_combustion_c_ddi,
                                                                    self.prop_electric_a_ddi,
                                                                    self.prop_electric_b_ddi])
        self.add_widget(self.prop_dropdown)

        self.dropdowns_and_items_to_str = {
            self.tire_20_ddi: "tire_20_setting",
            self.tire_22_ddi: "tire_22_setting",
            self.tire_18_ddi: "tire_18_setting",
            self.tire_19_ddi: "tire_19_setting",
            self.interior_modern_ddi: "interior_modern_setting",
            self.interior_vintage_ddi: "interior_vintage_setting",
            self.interior_sport_ddi: "interior_sport_setting",
            self.prop_combustion_a_ddi: "combustion_engine_a_setting",
            self.prop_combustion_b_ddi: "combustion_engine_b_setting",
            self.prop_combustion_c_ddi: "combustion_engine_c_setting",
            self.prop_electric_a_ddi: "electric_motor_a_setting",
            self.prop_electric_b_ddi: "electric_motor_b_setting",
            self.car_dropdown: "car_dropdown",
            self.tire_dropdown: "tire_dropdown",
            self.interior_dropdown: "interior_dropdown",
            self.prop_dropdown: "propulsion_dropdown"
        }

        # Setup data structures
        self.dropdowns = [self.car_dropdown,
                          self.tire_dropdown,
                          self.interior_dropdown,
                          self.prop_dropdown]
        self.opened_dd_index = None
        self.ddi_state_from_settings: Dict[DropdownItem, int] = {}

        # Add show configuration button and window
        self.popup = CarConfiguratorPopup(self)
        self.add_child(self.popup)
        self.show_config_button = Button(self.BUTTON_BB, self.display_configuration)

        self.set_reward_children([self.popup])

    @property
    def reward_template(self):
        return {
            "tire_20_setting": [False, True],
            "tire_22_setting": [False, True],
            "tire_18_setting": [False, True],
            "tire_19_setting": [False, True],
            "interior_modern_setting": [False, True],
            "interior_vintage_setting": [False, True],
            "interior_sport_setting": [False, True],
            "combustion_engine_a_setting": [False, True],
            "combustion_engine_b_setting": [False, True],
            "combustion_engine_c_setting": [False, True],
            "electric_motor_a_setting": [False, True],
            "electric_motor_b_setting": [False, True],
            "car_dropdown": {
                "opened": 0,
                "selected": [Car.A, Car.B, Car.C],
                "used_in_display": [Car.A, Car.B, Car.C]
            },
            "tire_dropdown": {
                "opened": 0,
                "selected": [TireSize.TIRE_20, TireSize.TIRE_22, TireSize.TIRE_18, TireSize.TIRE_19],
                "used_in_display": [TireSize.TIRE_20, TireSize.TIRE_22, TireSize.TIRE_18, TireSize.TIRE_19]
            },
            "interior_dropdown": {
                "opened": 0,
                "selected": [Interior.MODERN, Interior.VINTAGE, Interior.SPORT],
                "used_in_display": [Interior.MODERN, Interior.VINTAGE, Interior.SPORT]
            },
            "propulsion_dropdown": {
                "opened": 0,
                "selected": [
                    PropulsionSystem.COMBUSTION_ENGINE_A,
                    PropulsionSystem.COMBUSTION_ENGINE_B,
                    PropulsionSystem.COMBUSTION_ENGINE_C,
                    PropulsionSystem.ELECTRIC_MOTOR_A,
                    PropulsionSystem.ELECTRIC_MOTOR_B
                ],
                "used_in_display": [
                    PropulsionSystem.COMBUSTION_ENGINE_A,
                    PropulsionSystem.COMBUSTION_ENGINE_B,
                    PropulsionSystem.COMBUSTION_ENGINE_C,
                    PropulsionSystem.ELECTRIC_MOTOR_A,
                    PropulsionSystem.ELECTRIC_MOTOR_B
                ]
            }
        }

    def reset(self):
        self.popup.close()

        all_items = (self.car_dropdown.get_all_items()
                     + self.tire_dropdown.get_all_items()
                     + self.interior_dropdown.get_all_items()
                     + self.prop_dropdown.get_all_items())

        for item in all_items:
            item.set_visible(1)

        self.car_dropdown.close()
        self.tire_dropdown.close()
        self.interior_dropdown.close()
        self.prop_dropdown.close()

        self.opened_dd_index = None
        self.ddi_state_from_settings: Dict[DropdownItem, int] = {}

        self.reset_car_configurator_dropdowns()

    def set_selectable_options(self, dropdown_item: DropdownItem, selected: int):
        dropdown_item.set_visible(selected)

        self.register_selected_reward([self.dropdowns_and_items_to_str[dropdown_item], bool(selected)])

    def handle_click(self, click_position: np.ndarray):
        if self.is_popup_open():
            self.popup.handle_click(click_position)
            return

        if self.opened_dd_index is not None:
            dropdown = self.dropdowns[self.opened_dd_index]

            dropdown_value_clicked = False
            if dropdown.is_clicked_by(click_position):
                dropdown_value_clicked = True

            dropdown.handle_click(click_position)

            if dropdown_value_clicked:
                self._update_dropdowns_on_dropdown_value_click(self.opened_dd_index)
                chosen_option = dropdown.get_current_value()
                self.register_selected_reward([self.dropdowns_and_items_to_str[dropdown], "selected", chosen_option])

            self.opened_dd_index = None
            return

        # Show configuration button is only visible, if a value has been selected
        # in the last dropdown (i.e. the state of that dropdown is 1 and not 0)
        if (self.get_state()[len(self.dropdowns) - 1] != 0
                and self.show_config_button.is_clicked_by(click_position)):
            self.show_config_button.handle_click(click_position)
            return

        # Open a dropdown, if it is visible and was clicked
        for index, dropdown in enumerate(self.dropdowns):
            if dropdown.is_clicked_by(click_position):
                if index == 0 or self._is_dropdown_value_selected(index - 1):
                    dropdown.handle_click(click_position)
                    if dropdown.is_open():
                        self.opened_dd_index = index
                        self.register_selected_reward([self.dropdowns_and_items_to_str[dropdown], "opened"])
                    return

    def find_nearest_clickable(self, click_position: np.ndarray, current_minimal_distance: float,
                               current_clickable: Clickable) -> Tuple[float, Clickable, np.ndarray]:
        current_minimal_distance, current_clickable, popup_click_position = self.popup.find_nearest_clickable(
            click_position, current_minimal_distance, current_clickable
        )

        for index, dropdown in enumerate(self.dropdowns):
            if index == 0 or self._is_dropdown_value_selected(index - 1):
                current_minimal_distance, current_clickable = dropdown.calculate_distance_to_click(
                    click_position, current_minimal_distance, current_clickable
                )

        if self._is_dropdown_value_selected(len(self.dropdowns) - 1):
            current_minimal_distance, current_clickable = self.show_config_button.calculate_distance_to_click(
                click_position, current_minimal_distance, current_clickable
            )

        if current_clickable == self.popup.ok_button:
            return current_minimal_distance, current_clickable, popup_click_position
        else:
            return current_minimal_distance, current_clickable, current_clickable.get_bb().get_click_point_inside_bb()

    def get_clickable_elements(self, clickable_elements: List[Clickable]) -> List[Clickable]:
        if self.popup.is_open():
            return self.popup.get_clickable_elements()

        if self.opened_dd_index is not None:
            return self.dropdowns[self.opened_dd_index].get_visible_items()

        # Car Dropdown could be disabled if all cars have been deselected in the settings, thus only add the car
        # dropdown if it has selectable DropdownItems
        if len(self.car_dropdown.get_visible_items()) > 0:
            clickable_elements.append(self.car_dropdown)

        # Order here is important because it is directly linked with the order in the state vector, see below
        possible_clickable_widgets = [self.tire_dropdown, self.interior_dropdown, self.prop_dropdown,
                                      self.show_config_button]

        # If the state_value is 1, the corresponding widget is visible and can thus be clicked
        for state_value, widget in zip(self.get_state(), possible_clickable_widgets):
            if state_value:
                clickable_elements.append(widget)

        return clickable_elements

    def display_configuration(self):
        car = self.car_dropdown.get_current_value()
        tire_size = self.tire_dropdown.get_current_value()
        interior = self.interior_dropdown.get_current_value()
        propulsion_system = self.prop_dropdown.get_current_value()

        self.register_selected_reward([
            self.dropdowns_and_items_to_str[self.car_dropdown], "used_in_display", car
        ])
        self.register_selected_reward([
            self.dropdowns_and_items_to_str[self.tire_dropdown], "used_in_display", tire_size
        ])
        self.register_selected_reward([
            self.dropdowns_and_items_to_str[self.interior_dropdown], "used_in_display", interior
        ])
        self.register_selected_reward([
            self.dropdowns_and_items_to_str[self.prop_dropdown], "used_in_display", propulsion_system
        ])

        self.popup.open()

    def _update_dropdowns_on_dropdown_value_click(self, index: int) -> None:
        """Updates all dropdowns (sets visibility and/or initial selected item) when a dropdown
        value is clicked (i.e. dropdown.is_open() and dropdown.is_clicked_by(click_position))."""
        dropdown = self.dropdowns[index]
        # adjust shown dropdowns when a dropdown value is clicked
        self.get_state()[index] = 1  # set dropdown-value selected to true
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

    def reset_car_configurator_dropdowns(self):
        """Resets all dropdowns/hides all dropdowns but the first."""
        self.opened_dd_index = None

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


class CarConfiguratorPopup(Page, RewardElement):
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
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.ok_button = Button(self.OK_BUTTON_BB, self.close)
        self.car_configurator = car_configurator

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def find_nearest_clickable(self, click_position: np.ndarray, current_minimal_distance: float,
                               current_clickable: Clickable) -> Tuple[float, Clickable, np.ndarray]:
        if self.is_open():
            current_minimal_distance, current_clickable = self.ok_button.calculate_distance_to_click(
                click_position, current_minimal_distance, current_clickable
            )

            return current_minimal_distance, current_clickable, current_clickable.get_bb().get_click_point_inside_bb()

        return current_minimal_distance, current_clickable, click_position

    def get_clickable_elements(self) -> List[Clickable]:
        return [self.ok_button]

    def open(self) -> None:
        """Opens this popup."""
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close(self) -> None:
        """Closes this popup."""
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

        self.car_configurator.reset_car_configurator_dropdowns()

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]

    def render(self, img: np.ndarray):
        img = super().render(img)
        x, y, _, height = self.CONFIGURATION_TEXT_BB.get_as_tuple()
        props = [
            f"Propulsion System: {self.car_configurator.prop_dropdown.get_current_value().value}",
            f"Interior: {self.car_configurator.interior_dropdown.get_current_value().value}",
            f"Tires: {self.car_configurator.tire_dropdown.get_current_value().value}",
            f"Car: {self.car_configurator.car_dropdown.get_current_value().value}"
        ]

        space = 16
        for i, prop in enumerate(props):
            bottom_left_corner = (x, y + height - i * space)
            put_text(img, prop, bottom_left_corner, font_scale=0.4)
        return img
