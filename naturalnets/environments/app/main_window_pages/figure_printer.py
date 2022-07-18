import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.enums import Color, Figure
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.utils import render_onto_bb
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem

class FigurePrinter(Page):
    """The figure-printer page in the main-window.

       State description:
            state[0]: Denotes if a figure is currently shown.
    """

    STATE_LEN = 1
    IMG_PATH = IMAGES_PATH + "figure_printer.png"
    DROPDOWN_BB = BoundingBox(125, 348, 303, 22)
    DRAW_FIGURE_BUTTON_BB = BoundingBox(125, 406, 303, 22)
    FIGURE_CANVAS_BB = BoundingBox(125, 39, 303, 303)

    def __init__(self):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        self._figure_color:Color = None
        self.christmas_tree_ddi = DropdownItem(Figure.CHRISTMAS_TREE, display_name="Christmas Tree")
        self.space_ship_ddi = DropdownItem(Figure.SPACE_SHIP, display_name="Space Ship")
        self.guitar_ddi = DropdownItem(Figure.GUITAR, display_name="Guitar")
        self.house_ddi = DropdownItem(Figure.HOUSE, display_name="House")
        ddis = [self.christmas_tree_ddi, self.space_ship_ddi, self.guitar_ddi, self.house_ddi]
        self.dropdown = Dropdown(self.DROPDOWN_BB, ddis)

        # set initial state
        self.dropdown.set_selected_item(self.christmas_tree_ddi)
        self.dropdown.set_visible(self.space_ship_ddi, 0)
        self.dropdown.set_visible(self.guitar_ddi, 0)
        self.dropdown.set_visible(self.house_ddi, 0)
        self.current_figure = None

        self.add_widget(self.dropdown)

        self._draw_figure_button = Button(self.DRAW_FIGURE_BUTTON_BB, lambda: self._draw_figure())

    def _draw_figure(self):
        figure = self.dropdown.get_current_value()
        if figure is None:
            raise ValueError("Figure dropdown should have a value.")
        self.current_figure = figure
        self._show_figure(True)

    def set_dd_item_visible(self, item, visible):
        self.dropdown.set_visible(item, visible)
        if visible == True:
            # update selected item when a new item becomes visible
            self.dropdown.set_selected_item(self.dropdown.get_visible_items()[0])

    def _show_figure(self, show:bool):
        self.get_state()[0] = show

    def is_figure_shown(self):
        return self.get_state()[0]

    def set_figure_color(self, color:Color):
        self._figure_color = color

    def is_dropdown_open(self) -> bool:
        return self.dropdown.is_open()

    def handle_click(self, click_position):
        if self.dropdown.is_clicked_by(click_position) or self.dropdown.is_open():
            self.dropdown.handle_click(click_position)
        elif self._draw_figure_button.is_clicked_by(click_position):
            self._draw_figure()
        #TODO
        #print("Figure printer current color is", self._figure_color)

    def render(self, img: np.ndarray):
        super().render(img)
        if self.is_figure_shown() and self.current_figure is not None:
            figure_img_path = IMAGES_PATH + self.current_figure.value
            img = render_onto_bb(img, self.FIGURE_CANVAS_BB, cv2.imread(figure_img_path))
        return img
