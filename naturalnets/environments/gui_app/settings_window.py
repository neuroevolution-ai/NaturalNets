from typing import Dict, List

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.main_window import MainWindow
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.settings_window_pages.calculator_settings import CalculatorSettings
from naturalnets.environments.gui_app.settings_window_pages.car_configurator_settings import CarConfiguratorSettings
from naturalnets.environments.gui_app.settings_window_pages.figure_printer_settings import FigurePrinterSettings
from naturalnets.environments.gui_app.settings_window_pages.text_printer_settings import TextPrinterSettings
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.utils import get_group_bounding_box, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button


class SettingsWindow(StateElement, Clickable):
    """The settings window ot the app, containing the different settings-pages, one for
    each page of the main-window pages.

       State description:
            state[0]: the opened-state of the settings window.
            state[i]: represents the selected/shown status of page i, i in {1,..,4}.
    """
    STATE_LEN: int = 5
    BOUNDING_BOX = BoundingBox(3, 1, 422, 367)

    PAGE_BB = BoundingBox(25, 48, 378, 262)
    CLOSE_BUTTON_BB = BoundingBox(25, 318, 377, 27)

    TEXT_PRINTER_TAB_BUTTON_BB = BoundingBox(25, 25, 85, 23)
    CALCULATOR_TAB_BUTTON_BB = BoundingBox(111, 25, 79, 23)
    CAR_CONFIGURATOR_TAB_BUTTON_BB = BoundingBox(191, 25, 85, 23)
    FIGURE_PRINTER_TAB_BUTTON_BB = BoundingBox(277, 25, 97, 23)

    def __init__(self, main_window: MainWindow):
        super().__init__(self.STATE_LEN)
        self._bounding_box = self.BOUNDING_BOX

        self.text_printer_settings = TextPrinterSettings(main_window.text_printer)
        self.calculator_settings = CalculatorSettings(main_window.calculator)
        self.car_config_settings = CarConfiguratorSettings(main_window.car_configurator)
        self.figure_printer_settings = FigurePrinterSettings(main_window)

        self.close_button = Button(self.CLOSE_BUTTON_BB, self.close)

        self.tabs: List[Page] = [self.text_printer_settings,
                                 self.calculator_settings,
                                 self.car_config_settings,
                                 self.figure_printer_settings]

        self.tab_buttons: List[Button] = [
            Button(self.TEXT_PRINTER_TAB_BUTTON_BB,
                   lambda: self.set_current_tab(self.text_printer_settings)),
            Button(self.CALCULATOR_TAB_BUTTON_BB,
                   lambda: self.set_current_tab(self.calculator_settings)),
            Button(self.CAR_CONFIGURATOR_TAB_BUTTON_BB,
                   lambda: self.set_current_tab(self.car_config_settings)),
            Button(self.FIGURE_PRINTER_TAB_BUTTON_BB,
                   lambda: self.set_current_tab(self.figure_printer_settings)),
        ]

        self.tabs_bb: BoundingBox = self.get_tabs_bb(self.tab_buttons)
        self.tabs_to_state_index: Dict[Page, int] = {
            tab: index + 1 for index, tab in enumerate(self.tabs)
        }

        self.tabs_to_str: Dict[Page, str] = {
            self.text_printer_settings: "text_printer_settings_opened",
            self.calculator_settings: "calculator_settings_opened",
            self.car_config_settings: "car_config_settings_opened",
            self.figure_printer_settings: "figure_printer_settings_opened"
        }

        self.current_tab = None
        self.set_current_tab(self.text_printer_settings)
        self.add_children(self.tabs)

        self.reward_dict = {}
        self.reset_reward_dict()

    def reset_reward_dict(self):
        self.text_printer_settings.reset_reward_dict()
        self.calculator_settings.reset_reward_dict()
        self.car_config_settings.reset_reward_dict()
        self.figure_printer_settings.reset_reward_dict()

        self.reward_dict = {
            "open_settings_window": 0,
            "close_settings_window": 0,
            "text_printer_settings_opened": 0,
            "calculator_settings_opened": 0,
            "car_config_settings_opened": 0,
            "figure_printer_settings_opened": 0,
            self.text_printer_settings.__class__.__name__: self.text_printer_settings.reward_dict,
            self.calculator_settings.__class__.__name__: self.calculator_settings.reward_dict,
            self.car_config_settings.__class__.__name__: self.car_config_settings.reward_dict,
            self.figure_printer_settings.__class__.__name__: self.figure_printer_settings.reward_dict
        }

    def is_open(self) -> int:
        """Returns if the settings window is open."""
        return self.get_state()[0]

    def open(self):
        """Opens the settings window."""
        self.reward_dict["open_settings_window"] = 1
        self.get_state()[0] = 1

    def close(self):
        """Closes the settings window."""
        self.reward_dict["close_settings_window"] = 1
        self.get_state()[0] = 0

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def handle_click(self, click_position: np.ndarray):
        # Check if current page is blocking click or click in current page bounding-box
        # (needs to be checked here since e.g. an opened dropdown should prevent a click
        # on the close button of the settings window)
        if (self.current_tab.is_popup_open()
                or self.current_tab.is_dropdown_open()
                or self.PAGE_BB.is_point_inside(click_position)):
            self.current_tab.handle_click(click_position)
            return

        # Check if close button clicked
        if self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
            return

        # Check if menu (tab-buttons) are clicked
        if self.tabs_bb.is_point_inside(click_position):
            self.handle_tabs_button_click(click_position)
            return

    def handle_tabs_button_click(self, click_position: np.ndarray) -> None:
        """Handles a click inside the menu bounding-box (performing the hit menu-button's action,
        if any).

        Args:
            click_position (np.ndarray): the click position (inside the menu-bounding-box).
        """
        for tab in self.tab_buttons:
            if tab.is_clicked_by(click_position):
                tab.handle_click(click_position)

    def set_current_tab(self, current_tab: Page):
        """Sets the currently selected/shown page/tab, setting the respective
        state element to 1 and the state elements representing the other pages/tabs
        to 0.

        Args:
            current_tab (Page): the page/tab to be selected.
        """
        for tab, index in self.tabs_to_state_index.items():
            if tab == current_tab:
                # If current_tab is None then this function is called on __init__ and we do not want
                # to give reward for this (i.e. change the reward dict)
                if self.current_tab is not None:
                    self.reward_dict[self.tabs_to_str[current_tab]] = 1

                self.get_state()[index] = 1
                self.current_tab = current_tab
            else:
                self.get_state()[index] = 0

    def render(self, img: np.ndarray) -> np.ndarray:
        """ Renders the main window and all its children onto the given image.
        """
        to_render = cv2.imread(self.current_tab.get_img_path())
        img = render_onto_bb(img, self.get_bb(), to_render)
        self.current_tab.render(img)
        return img

    def get_tabs_bb(self, tab_buttons: List[Button]) -> BoundingBox:
        """Returns the bounding-box of the tabs-menu (bounding-box of all buttons)."""
        return get_group_bounding_box(tab_buttons)
