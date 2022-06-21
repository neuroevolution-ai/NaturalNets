import cv2
import numpy as np

from cmath import inf
from typing import List
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.interfaces import Clickable, HasPopups
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.settings_window_pages.calculator_settings import CalculatorSettings
from naturalnets.environments.app.settings_window_pages.car_configurator_settings import CarConfiguratorSettings
from naturalnets.environments.app.settings_window_pages.figure_printer_settings import FigurePrinterSettings
from naturalnets.environments.app.settings_window_pages.text_printer_settings import TextPrinterSettings
from naturalnets.environments.app.state_element import StateElement
from naturalnets.environments.app.utils import get_group_bounding_box, render_onto_bb

class SettingsWindow(StateElement, Clickable, HasPopups):
    STATE_LEN:int = 5
    BOUNDING_BOX = BoundingBox(3, 1, 422, 367)

    CLOSE_BUTTON_BB = BoundingBox(25, 318, 377, 27)

    TEXT_PRINTER_TAB_BUTTON_BB = BoundingBox(25, 25, 85, 23)
    CALCULATOR_TAB_BUTTON_BB = BoundingBox(111, 25, 79, 23)
    CAR_CONFIGURATOR_TAB_BUTTON_BB = BoundingBox(191, 25, 85, 23)
    FIGURE_PRINTER_TAB_BUTTON_BB = BoundingBox(277, 25, 97, 23)

    def __init__(self):
        super().__init__(self.STATE_LEN)
        self._bounding_box = self.BOUNDING_BOX

        self.text_printer_settings = TextPrinterSettings()
        self.calculator_settings = CalculatorSettings()
        self.car_config_settings = CarConfiguratorSettings()
        self.figure_printer_settings = FigurePrinterSettings()

        self.close_button = Button(self.CLOSE_BUTTON_BB, lambda: self.close())

        self.tabs:list[Page] = [self.text_printer_settings, self.calculator_settings, self.car_config_settings, self.figure_printer_settings]

        self.tab_buttons:list[Button] = [
            Button(self.TEXT_PRINTER_TAB_BUTTON_BB, lambda: self.set_current_tab(self.text_printer_settings)),
            Button(self.CALCULATOR_TAB_BUTTON_BB, lambda: self.set_current_tab(self.calculator_settings)),
            Button(self.CAR_CONFIGURATOR_TAB_BUTTON_BB, lambda: self.set_current_tab(self.car_config_settings)),
            Button(self.FIGURE_PRINTER_TAB_BUTTON_BB, lambda: self.set_current_tab(self.figure_printer_settings)),
        ]

        self.tabs_bb:BoundingBox = self.get_tabs_bb(self.tab_buttons)

        # self.get_state()[0] represents the opened-state of the settings window
        #assert len(self.tabs) == self.get_state_len() - 1
        self.tabs_to_state_index:dict[Page, int] = {tab: index + 1 for index, tab in enumerate(self.tabs)}

        self.set_current_tab(self.text_printer_settings)

        self.add_child(self.text_printer_settings)
        self.add_child(self.figure_printer_settings)

    def get_text_printer_settings(self):
        return self.text_printer_settings

    def get_calculator_settings(self):
        return self.calculator_settings

    def get_car_configurator_settings(self):
        return self.car_config_settings

    def get_figure_printer_settings(self):
        return self.figure_printer_settings

    def is_open(self) -> int:
        return self.get_state()[0]

    def open(self):
        self.get_state()[0] = 1

    def close(self):
        self.get_state()[0] = 0

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def is_popup_open(self) -> bool:
        is_any_popup_open = False
        is_any_popup_open |= self.get_text_printer_settings().is_popup_open()
        is_any_popup_open |= self.get_calculator_settings().is_popup_open()
        is_any_popup_open |= self.get_car_configurator_settings().is_popup_open()
        is_any_popup_open |= self.get_figure_printer_settings().is_popup_open()
        return is_any_popup_open


    def handle_click(self, click_position: np.ndarray):
        if self.is_popup_open():
            self.current_tab.handle_click(click_position)

        elif self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click()

        elif self.tabs_bb.is_point_inside(click_position):
            self.handle_tabs_button_click(click_position)

        else:
            self.current_tab.handle_click(click_position)

    def handle_tabs_button_click(self, click_position:np.ndarray) -> None:
        for tab in self.tab_buttons:
            if tab.is_clicked_by(click_position):
                tab.handle_click()

    def set_current_tab(self, current_tab:Page):
        for tab, index in self.tabs_to_state_index.items():
            if tab == current_tab:
                self.get_state()[index] = 1
                self.current_tab = current_tab
            else:
                self.get_state()[index] = 0

    def render(self, img:np.ndarray) -> np.ndarray:
        to_render = cv2.imread(self.current_tab.get_img_path())
        img = render_onto_bb(img, self.get_bb(), to_render)
        self.current_tab.render(img)
        return img

    def get_tabs_bb(self, tab_buttons:List[Button]) -> BoundingBox:
        return get_group_bounding_box(tab_buttons)


