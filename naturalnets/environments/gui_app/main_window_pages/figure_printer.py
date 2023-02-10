import os
from typing import List

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.gui_app.enums import Color, Figure
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem


class FigurePrinter(Page, RewardElement):
    """The figure-printer page in the main-window.

       State description:
            state[0]: Denotes if a figure is currently shown.
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "figure_printer.png")
    DROPDOWN_BB = BoundingBox(125, 348, 303, 22)
    DRAW_FIGURE_BUTTON_BB = BoundingBox(125, 406, 303, 22)
    FIGURE_CANVAS_BB = BoundingBox(125, 39, 303, 303)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self._figure_color_from_settings: Color = Color.BLACK
        self.christmas_tree_ddi = DropdownItem(Figure.CHRISTMAS_TREE, display_name="Christmas Tree")
        self.space_ship_ddi = DropdownItem(Figure.SPACE_SHIP, display_name="Space Ship")
        self.guitar_ddi = DropdownItem(Figure.GUITAR, display_name="Guitar")
        self.house_ddi = DropdownItem(Figure.HOUSE, display_name="House")
        ddis = [self.christmas_tree_ddi, self.space_ship_ddi, self.guitar_ddi, self.house_ddi]
        self.dropdown = Dropdown(self.DROPDOWN_BB, ddis)

        self.dropdown_items_to_str = {
            self.christmas_tree_ddi: "christmas_tree_setting",
            self.space_ship_ddi: "space_ship_setting",
            self.guitar_ddi: "guitar_setting",
            self.house_ddi: "house_setting"
        }

        self.add_widget(self.dropdown)

        self._draw_figure_button = Button(self.DRAW_FIGURE_BUTTON_BB, self._draw_figure)
        self._rendered_figure_color: Color = None  # color rendered onto the image

        # Set initial state
        self.dropdown_opened = False
        self.current_figure = None

        self.reset()

    @property
    def reward_template(self):
        return {
            "christmas_tree_setting": [False, True],
            "guitar_setting": [False, True],
            "space_ship_setting": [False, True],
            "house_setting": [False, True],
            "figure_color": {
                "setting": [Color.BLACK, Color.GREEN, Color.BLUE, Color.BROWN],
                "used_in_display": [Color.BLACK, Color.GREEN, Color.BLUE, Color.BROWN]
            },
            "figure_dropdown": {
                "opened": 0,
                "selected": [Figure.CHRISTMAS_TREE, Figure.SPACE_SHIP, Figure.GUITAR, Figure.HOUSE],
                "used_in_display": [Figure.CHRISTMAS_TREE, Figure.SPACE_SHIP, Figure.GUITAR, Figure.HOUSE]
            }
        }

    def reset(self):
        self.dropdown.close()
        self.dropdown.set_selected_item(self.christmas_tree_ddi)
        self.dropdown_opened = False

        self.christmas_tree_ddi.set_visible(1)
        self.space_ship_ddi.set_visible(0)
        self.guitar_ddi.set_visible(0)
        self.house_ddi.set_visible(0)

        self.current_figure = None

        self._figure_color_from_settings: Color = Color.BLACK

        # Initially, the figure is not printed, thus reset the state using this function
        self._show_figure(0)

    def _draw_figure(self):
        figure = self.dropdown.get_current_value()
        if figure is None:
            raise ValueError("Figure dropdown should have a value.")
        self.current_figure = figure
        self._rendered_figure_color = self._figure_color_from_settings

        self.register_selected_reward(["figure_dropdown", "used_in_display", self.current_figure])
        self.register_selected_reward(["figure_color", "used_in_display", self._rendered_figure_color])

        self._show_figure(1)

    def set_dd_item_visible(self, item: DropdownItem, visible: int):
        """Sets the given dropdown-item's visibility. Used by
        text-printer settings."""
        item.set_visible(visible)

        self.register_selected_reward([self.dropdown_items_to_str[item], bool(visible)])

        # Update the item that is shown on the closed dropdown, if the dropdown previously did not have any entries
        if len(self.dropdown.get_visible_items()) != 0:
            self.dropdown.set_selected_item(self.dropdown.get_visible_items()[0])

    def _show_figure(self, show: int):
        self.get_state()[0] = show

    def is_figure_shown(self) -> int:
        return self.get_state()[0]

    def set_figure_color(self, color: Color):
        self._figure_color_from_settings = color

        self.register_selected_reward(["figure_color", "setting", color])

    def is_dropdown_open(self) -> int:
        return self.dropdown.is_open()

    def handle_click(self, click_position):
        # Check dropdown first, may obscure apply-button when opened
        if self.dropdown_opened:
            dropdown_value_clicked = False
            if self.dropdown.is_clicked_by(click_position):
                dropdown_value_clicked = True

            self.dropdown.handle_click(click_position)

            if dropdown_value_clicked:
                selected_item = self.dropdown.get_current_value()
                self.register_selected_reward(["figure_dropdown", "selected", selected_item])

            self.dropdown_opened = False
            return

        if self.dropdown.is_clicked_by(click_position):
            self.dropdown.handle_click(click_position)

            if self.dropdown.is_open():
                self.dropdown_opened = True
                self.register_selected_reward(["figure_dropdown", "opened"])

            return

        if self._draw_figure_button.is_clicked_by(click_position):
            self._draw_figure()

    def get_clickable_elements(self, clickable_elements: List[Clickable]) -> List[Clickable]:
        if self.dropdown_opened:
            return self.dropdown.get_visible_items()

        clickable_elements.append(self.dropdown)
        clickable_elements.append(self._draw_figure_button)

        return clickable_elements

    def render(self, img: np.ndarray):
        super().render(img)
        if self.is_figure_shown() and self.current_figure is not None:
            figure_img_path = os.path.join(IMAGES_PATH, self.current_figure.value)
            img = render_onto_bb(img, self.FIGURE_CANVAS_BB, cv2.imread(figure_img_path))

            # Indicate the selected color of the figure with a text string
            x, y, _, height = self.FIGURE_CANVAS_BB.get_as_tuple()
            padding = 10
            bottom_left_corner = (x + padding, y + height - padding)
            put_text(img, f"{self._rendered_figure_color}", bottom_left_corner, font_scale=0.4)
        return img
