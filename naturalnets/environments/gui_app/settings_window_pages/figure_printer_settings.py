import os
from typing import Dict, List, Tuple

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.main_window import MainWindow
from naturalnets.environments.gui_app.main_window_pages.figure_printer import Figure
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup


class FigurePrinterSettings(Page, RewardElement):
    """The figure-printer settings page, manipulates the figure-printer page."""
    STATE_LEN = 0
    MAX_CLICKABLE_ELEMENTS = 9

    IMG_PATH = os.path.join(IMAGES_PATH, "figure_printer_settings.png")

    SHOW_FIG_PRINTER_BB = BoundingBox(38, 91, 141, 14)

    # figure checkboxes bounding-boxes
    CHRISTMAS_TREE_BB = BoundingBox(38, 145, 103, 14)
    SPACE_SHIP_BB = BoundingBox(217, 145, 83, 14)
    GUITAR_BB = BoundingBox(38, 171, 54, 14)
    HOUSE_BB = BoundingBox(217, 171, 56, 14)

    # color_rbg bounding-boxes
    GREEN_RB_BB = BoundingBox(38, 225, 55, 14)
    BLUE_RB_BB = BoundingBox(38, 251, 47, 14)
    BLACK_RB_BB = BoundingBox(217, 225, 53, 14)
    BROWN_RB_BB = BoundingBox(217, 251, 57, 14)

    def __init__(self, main_window: MainWindow):
        Page.__init__(self, self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.main_window = main_window
        self.figure_printer = main_window.figure_printer

        self.popup = FigureCheckboxesPopup(self)
        self.add_child(self.popup)

        self._show_fig_printer_checkbox = CheckBox(self.SHOW_FIG_PRINTER_BB)

        self.add_widget(self._show_fig_printer_checkbox)

        self.figure_checkboxes, self.checkbox_to_figure = self._get_figure_checkboxes()
        self.figure_to_checkbox = {
            figure: checkbox for (checkbox, figure) in self.checkbox_to_figure.items()
        }
        self.add_widgets(self.figure_checkboxes)

        self._color_rbg, self._button_to_color = self._get_color_rbg()
        self.add_widget(self._color_rbg)

        self.set_reward_children([self.popup])

    @property
    def reward_template(self):
        return {
            "activate_figure_printer": [False, True]
        }

    def reset(self):
        self.popup.close()
        self.popup.reset()

        self._show_fig_printer_checkbox.set_selected(0)

        for checkbox in self.figure_checkboxes:
            if self.checkbox_to_figure[checkbox] == Figure.CHRISTMAS_TREE:
                checkbox.set_selected(1)
            else:
                checkbox.set_selected(0)

        for button in self._color_rbg.radio_buttons:
            if self._button_to_color[button] == Color.BLACK:
                self._color_rbg.set_selected_button(button)

    def _get_figure_checkboxes(self) -> Tuple[List[CheckBox], Dict[CheckBox, Figure]]:
        figure_checkboxes = []
        christmas_tree_checkbox = CheckBox(
            self.CHRISTMAS_TREE_BB,
            lambda is_checked: self.figure_printer.set_dd_item_visible(
                self.figure_printer.christmas_tree_ddi, is_checked
            )
        )
        space_ship_checkbox = CheckBox(
            self.SPACE_SHIP_BB,
            lambda is_checked: self.figure_printer.set_dd_item_visible(
                self.figure_printer.space_ship_ddi, is_checked
            )
        )
        guitar_checkbox = CheckBox(
            self.GUITAR_BB,
            lambda is_checked: self.figure_printer.set_dd_item_visible(
                self.figure_printer.guitar_ddi, is_checked
            )
        )
        house_checkbox = CheckBox(
            self.HOUSE_BB,
            lambda is_checked: self.figure_printer.set_dd_item_visible(
                self.figure_printer.house_ddi, is_checked
            )
        )

        figure_checkboxes.append(christmas_tree_checkbox)
        figure_checkboxes.append(space_ship_checkbox)
        figure_checkboxes.append(guitar_checkbox)
        figure_checkboxes.append(house_checkbox)

        checkbox_to_figure = {
            christmas_tree_checkbox: Figure.CHRISTMAS_TREE,
            space_ship_checkbox: Figure.SPACE_SHIP,
            guitar_checkbox: Figure.GUITAR,
            house_checkbox: Figure.HOUSE,
        }

        return figure_checkboxes, checkbox_to_figure

    def _get_color_rbg(self) -> Tuple[RadioButtonGroup, Dict[RadioButton, Color]]:
        black_rb = RadioButton(self.BLACK_RB_BB)
        green_rb = RadioButton(self.GREEN_RB_BB)
        blue_rb = RadioButton(self.BLUE_RB_BB)
        brown_rb = RadioButton(self.BROWN_RB_BB)

        button_to_color = {
            black_rb: Color.BLACK,
            green_rb: Color.GREEN,
            blue_rb: Color.BLUE,
            brown_rb: Color.BROWN
        }

        rbg = RadioButtonGroup([black_rb, green_rb, blue_rb, brown_rb])

        return rbg, button_to_color

    def get_figure_color(self) -> Color:
        return self._button_to_color[self._color_rbg.get_selected_radio_button()]

    def get_figures(self) -> List[Figure]:
        selected_figures = []
        for checkbox in self.figure_checkboxes:
            if checkbox.is_selected():
                selected_figures.append(self.checkbox_to_figure[checkbox])

        return selected_figures

    def is_figure_printer_activated(self) -> int:
        return self._show_fig_printer_checkbox.is_selected()

    def is_popup_open(self) -> int:
        return self.popup.is_open()

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.is_popup_open():
            self.popup.handle_click(click_position)
            return

        if self._show_fig_printer_checkbox.is_clicked_by(click_position):
            self._show_fig_printer_checkbox.handle_click(click_position)
            figure_printer_activated = self.is_figure_printer_activated()
            self.main_window.enable_figure_printer(figure_printer_activated)

            self.register_selected_reward(["activate_figure_printer", bool(figure_printer_activated)])

            # Change current main window page if it was the figure printer and the figure printer
            # has been deactivated
            if (self.main_window.get_current_page() == self.main_window.figure_printer
                    and not self._show_fig_printer_checkbox.is_selected()):
                self.main_window.set_current_page(self.main_window.text_printer)
            return

        # other widgets only available when figure printer is activated
        if self.is_figure_printer_activated():
            if self._color_rbg.get_bb().is_point_inside(click_position):
                self._color_rbg.handle_click(click_position)
                self.figure_printer.set_figure_color(self.get_figure_color())
            else:
                for checkbox in self.figure_checkboxes:
                    if checkbox.is_clicked_by(click_position):
                        checkbox.handle_click(click_position)
                        break
                if self.get_selected_checkboxes_count() == 0:
                    self.popup.open()

    def get_selected_checkboxes_count(self) -> int:
        return sum(checkbox.is_selected() for checkbox in self.figure_checkboxes)

    def select_figure_checkbox(self, figure: Figure):
        self.figure_to_checkbox[figure].set_selected(1)

    def set_figure_printer_dd_value(self, figure: Figure):
        self.figure_printer.dropdown.set_selected_value(figure)

    def render(self, img: np.ndarray):
        img = super().render(img)
        if self.popup.is_open():
            img = self.popup.render(img)
        return img

    def get_clickable_elements(self, clickable_elements: List[Clickable]) -> List[Clickable]:
        if self.popup.is_open():
            return self.popup.get_clickable_elements()

        clickable_elements.append(self._show_fig_printer_checkbox)

        # If the "Activate FigurePrinter" checkbox is not activated, it is the only clickable
        # widget, thus return
        if not self.is_figure_printer_activated():
            return clickable_elements

        clickable_elements.extend(self.figure_checkboxes)
        clickable_elements.extend(self._color_rbg.get_radio_buttons())

        return clickable_elements


class FigureCheckboxesPopup(Page, RewardElement):
    """Popup for the figure-printer settings (pops up when no figure-checkbox is selected).

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1
    MAX_CLICKABLE_ELEMENTS = 2

    BOUNDING_BOX = BoundingBox(14, 87, 381, 114)
    IMG_PATH = os.path.join(IMAGES_PATH, "figure_settings_checkboxes_popup.png")

    APPLY_BUTTON_BB = BoundingBox(103, 157, 203, 22)
    DROPDOWN_BB = BoundingBox(36, 129, 337, 22)

    def __init__(self, figure_printer_settings: FigurePrinterSettings):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.apply_button = Button(self.APPLY_BUTTON_BB, self.close)
        self.figure_printer_settings = figure_printer_settings

        self.christmas_tree_ddi = DropdownItem(Figure.CHRISTMAS_TREE, display_name="Christmas Tree")
        space_ship_ddi = DropdownItem(Figure.SPACE_SHIP, display_name="Space Ship")
        guitar_ddi = DropdownItem(Figure.GUITAR, display_name="Guitar")
        house_ddi = DropdownItem(Figure.HOUSE, display_name="House")
        ddis = [self.christmas_tree_ddi, space_ship_ddi, guitar_ddi, house_ddi]
        self.dropdown = Dropdown(self.DROPDOWN_BB, ddis)
        self.add_widget(self.dropdown)

        self.dropdown_opened = False

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"],
            "dropdown": {
                "opened": 0,
                "selected": [
                    Figure.CHRISTMAS_TREE,
                    Figure.SPACE_SHIP,
                    Figure.GUITAR,
                    Figure.HOUSE
                ]
            }
        }

    def reset(self):
        self.dropdown.close()
        self.dropdown_opened = False
        self.dropdown.set_selected_item(self.christmas_tree_ddi)

    def handle_click(self, click_position: np.ndarray) -> None:
        # Check dropdown first, may obscure apply-button when opened
        if self.dropdown_opened:
            dropdown_value_clicked = False
            if self.dropdown.is_clicked_by(click_position):
                dropdown_value_clicked = True

            self.dropdown.handle_click(click_position)

            if dropdown_value_clicked:
                selected_item = self.dropdown.get_current_value()
                self.register_selected_reward(["dropdown", "selected", selected_item])

            self.dropdown_opened = False
            return

        if self.dropdown.is_clicked_by(click_position):
            self.dropdown.handle_click(click_position)

            if self.dropdown.is_open():
                self.dropdown_opened = True
                self.register_selected_reward(["dropdown", "opened"])

            return

        if self.apply_button.is_clicked_by(click_position):
            self.apply_button.handle_click(click_position)
            curr_dropdown_value: Figure = self.dropdown.get_current_value()

            assert curr_dropdown_value is not None  # Popup dropdown value should never be None

            self.figure_printer_settings.select_figure_checkbox(curr_dropdown_value)
            self.figure_printer_settings.set_figure_printer_dd_value(curr_dropdown_value)

    def open(self):
        """Opens this popup."""
        self.get_state()[0] = 1
        self.dropdown.set_selected_item(self.christmas_tree_ddi)

        self.register_selected_reward(["popup", "open"])

    def close(self):
        """Closes this popup."""
        self.get_state()[0] = 0

        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]

    def get_clickable_elements(self) -> List[Clickable]:
        if self.dropdown_opened:
            return [self.dropdown]

        return [self.dropdown, self.apply_button]
