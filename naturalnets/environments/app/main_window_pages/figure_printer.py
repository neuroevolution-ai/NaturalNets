import cv2
import numpy as np

from enum import Enum
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.colors import Color
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.utils import render_onto_bb
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem

class Figure(Enum):
    CHRISTMAS_TREE = "figure_christmas_tree.png"
    SPACE_SHIP = "figure_space_ship.png"
    GUITAR = "figure_guitar.png"
    HOUSE = "figure_house.png"

class FigurePrinter(Page):

    STATE_LEN = 3
    IMG_PATH = IMAGES_PATH + "figure_printer.png"
    DROPDOWN_BB = BoundingBox(125, 348, 303, 22)
    DRAW_FIGURE_BUTTON_BB = BoundingBox(125, 406, 303, 22)
    FIGURE_CANVAS_BB = BoundingBox(125, 39, 303, 303)

    def __init__(self):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        self._figure_color:Color = None
        self.christmas_tree_ddi = DropdownItem(Figure.CHRISTMAS_TREE)
        self.space_ship_ddi = DropdownItem(Figure.SPACE_SHIP)
        self.guitar_ddi = DropdownItem(Figure.GUITAR)
        self.house_ddi = DropdownItem(Figure.HOUSE)
        ddis = [self.christmas_tree_ddi, self.space_ship_ddi, self.guitar_ddi, self.house_ddi]

        self.dropdown = Dropdown(self.DROPDOWN_BB, ddis)
        self.dropdown.set_selected_item(self.christmas_tree_ddi)
        self.current_figure = None
        self.add_widget(self.dropdown)

        self._draw_figure_button = Button(self.DRAW_FIGURE_BUTTON_BB, lambda: self.draw_figure())

    def _draw_figure(self):
        figure = self.dropdown.get_current_value()
        if figure is None:
            raise ValueError("Figure dropdown should have a value.")
        self._set_figure_state(figure)
        self.current_figure = figure
        self._show_figure(True)
        
    def _set_figure_state(self, figure:Figure):
        if figure == Figure.CHRISTMAS_TREE:
            self.get_state()[1:3] = np.array([0,0], dtype=int)
        elif figure == Figure.SPACE_SHIP:
            self.get_state()[1:3] = np.array([0,1], dtype=int)
        elif figure == Figure.GUITAR:
            self.get_state()[1:3] = np.array([1,0], dtype=int)
        elif figure == Figure.HOUSE:
            self.get_state()[1:3] = np.array([1,1], dtype=int)

    def _show_figure(self, show:bool):
        self.get_state()[0] = show

    def is_figure_shown(self):
        return self.get_state()[0]

    def set_figure_color(self, color:Color):
        self._figure_color = color

    def handle_click(self, click_position):
        if self.dropdown.is_clicked_by(click_position):
            self.dropdown.handle_click(click_position)
        elif self._draw_figure_button.is_clicked_by(click_position):
            self._draw_figure()
        #TODO
        print("Figure printer current color is", self._figure_color)

    def render(self, img: np.ndarray):
        super().render(img)
        if self.is_figure_shown() and self.current_figure is not None:
            figure_img_path = IMAGES_PATH + self.current_figure.value
            img = render_onto_bb(img, self.FIGURE_CANVAS_BB, cv2.imread(figure_img_path))
        return img
