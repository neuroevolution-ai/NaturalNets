import os
from typing import List

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import IMAGES_PATH
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.main_window_pages.calculator import Calculator
from naturalnets.environments.gui_app.main_window_pages.car_configurator import CarConfigurator
from naturalnets.environments.gui_app.main_window_pages.figure_printer import FigurePrinter
from naturalnets.environments.gui_app.main_window_pages.text_printer import TextPrinter
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button


class MainWindow(StateElement, Clickable, RewardElement):
    """The main window of the app, containing the menu as well as the respective pages
    (text printer, calculator, car configurator and figure printer).

       State description:
            state[i]: represents the selected/shown status of page i, i in {0,..,3}.
    """

    STATE_LEN = 4
    MAX_CLICKABLE_ELEMENTS = 4

    IMG_PATH = os.path.join(IMAGES_PATH, "main_window_base.png")
    FIGURE_PRINTER_BUTTON_IMG_PATH = os.path.join(IMAGES_PATH, "figure_printer_button.png")
    BOUNDING_BOX = BoundingBox(0, 0, 448, 448)
    MENU_AREA_BB = BoundingBox(4, 25, 110, 118)
    PAGES_AREA_BB = BoundingBox(117, 22, 326, 420)

    TEXT_PRINTER_BUTTON_BB = BoundingBox(9, 28, 99, 22)
    CALCULATOR_BUTTON_BB = BoundingBox(9, 56, 99, 22)
    CAR_CONFIGURATOR_BUTTON_BB = BoundingBox(9, 84, 99, 22)
    FIGURE_PRINTER_BUTTON_BB = BoundingBox(9, 112, 99, 22)

    def __init__(self):
        StateElement.__init__(self, self.STATE_LEN)
        RewardElement.__init__(self)

        self._bounding_box = self.BOUNDING_BOX

        self.text_printer = TextPrinter()
        self.calculator = Calculator()
        self.car_configurator = CarConfigurator()
        self.figure_printer = FigurePrinter()

        self.pages: List[Page] = [self.text_printer, self.calculator,
                                  self.car_configurator, self.figure_printer]
        assert len(self.pages) == self.get_state_len()

        self.current_page = None

        self.is_figure_printer_button_visible = 0

        self.text_printer_btn = Button(self.TEXT_PRINTER_BUTTON_BB, lambda: self.set_current_page(self.text_printer))
        self.calculator_btn = Button(self.CALCULATOR_BUTTON_BB, lambda: self.set_current_page(self.calculator))
        self.car_configurator_btn = Button(
            self.CAR_CONFIGURATOR_BUTTON_BB, lambda: self.set_current_page(self.car_configurator)
        )
        self.figure_printer_btn = Button(
            self.FIGURE_PRINTER_BUTTON_BB,
            lambda: self.set_current_page(self.figure_printer)
        )

        self.buttons = [
            self.text_printer_btn,
            self.calculator_btn,
            self.car_configurator_btn,
            self.figure_printer_btn
        ]

        self.add_children([self.text_printer, self.calculator, self.car_configurator, self.figure_printer])
        self.set_reward_children([self.text_printer, self.calculator, self.car_configurator, self.figure_printer])

        self.pages_to_str = {
            self.text_printer: "text_printer",
            self.calculator: "calculator",
            self.car_configurator: "car_configurator",
            self.figure_printer: "figure_printer"
        }

    @property
    def reward_template(self):
        return {
            "page_selected": ["text_printer", "calculator", "car_configurator", "figure_printer"]
        }

    def reset(self):
        self.text_printer.reset()
        self.calculator.reset()
        self.car_configurator.reset()
        self.figure_printer.reset()

        self.is_figure_printer_button_visible = 0
        self.set_current_page(self.text_printer)

    def enable_figure_printer(self, visible: int) -> None:
        self.is_figure_printer_button_visible = visible

    def get_current_page(self):
        return self.current_page

    def set_current_page(self, page: Page):
        """Sets the currently selected/shown page, setting the respective
        state element to 1 and the state elements representing the other pages
        to 0.

        Args:
            page (Page): the page to be selected.
        """
        if self.current_page != page:
            self.get_state()[:] = 0
            self.get_state()[self.pages.index(page)] = 1
            self.current_page = page

            # noinspection PyTypeChecker
            self.register_selected_reward(["page_selected", self.pages_to_str[self.current_page]])

    def current_page_blocks_click(self) -> bool:
        """Returns true if the current page blocks clicks, i.e. has a dropdown/popup open.
        """
        return self.current_page.is_dropdown_open() or self.current_page.is_popup_open()

    def handle_click(self, click_position: np.ndarray) -> None:
        # Let the current page process the click, if the current page blocks clicks
        # to the main page (e.g. due to open dropdowns) or the click
        # is inside the bounding box of the current page.
        # Note that the settings menu button is handled in the AppController class.
        if self.current_page_blocks_click() or self.PAGES_AREA_BB.is_point_inside(click_position):
            self.current_page.handle_click(click_position)
            return
        # Check if menu is clicked
        if self.MENU_AREA_BB.is_point_inside(click_position):
            self.handle_menu_click(click_position)
            return

    def is_dropdown_open(self):
        """Returns true if the current page has an opened dropdown.
        """
        return self.current_page.is_dropdown_open()

    def handle_menu_click(self, click_position: np.ndarray) -> None:
        """Handles a click inside the menu bounding-box (performing the hit menu-button's action,
        if any).

        Args:
            click_position (np.ndarray): the click position (inside the menu-bounding-box).
        """
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                # check if figure printer button is visible
                if button != self.figure_printer_btn or self.is_figure_printer_button_visible:
                    button.handle_click(click_position)
                    break

    def render(self, img: np.ndarray):
        """ Renders the main window and all its children onto the given image.
        """
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.get_bb(), to_render)
        img = self.current_page.render(img)

        if self.is_figure_printer_button_visible:
            figure_printer_img = cv2.imread(self.FIGURE_PRINTER_BUTTON_IMG_PATH)
            img = render_onto_bb(img, self.FIGURE_PRINTER_BUTTON_BB, figure_printer_img)

        return img

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def get_clickable_elements(self, clickable_elements: List[Clickable]) -> List[Clickable]:
        clickable_elements.extend([
            self.text_printer_btn,
            self.calculator_btn,
            self.car_configurator_btn
        ])

        if self.is_figure_printer_button_visible == 1:
            clickable_elements.append(self.figure_printer_btn)

        return self.current_page.get_clickable_elements(clickable_elements)
