import numpy as np

from cmath import inf
from typing import List, Dict, Any
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.elements import Elements
from naturalnets.environments.app.state_manipulator import StateManipulator
from naturalnets.environments.app.text_printer_settings import TextPrinterSettings
from naturalnets.environments.app.widget import Widget

class SettingsWindow(StateManipulator):

    _STATE_LEN = 5
    _PAGES = [TextPrinterSettings]

    def __init__(self, state_sector:np.ndarray, pages_dict:Dict[Elements, Dict[str, Any]]):
        super().__init__(state_sector)
        # len(state_sector) = len(self.tabs) + 1 (self._is_openend flag)
        # 
        self.tabs_to_pages = {page_dict["navigator"]: page_dict["widgets"] for page_dict in pages_dict.values()}


        #self.tabs_to_pages = {
        #    Elements.SETTINGS_TEXT_PRINTER_TAB_BUTTON: pages_dict[Elements.SETTINGS_PAGE_TEXT_PRINTER],
        #    #Elements.SETTINGS_CALCULATOR_TAB_BUTTON: pages_dict[Elements.SETTINGS_PAGE_CALCULATOR],
        #    #Elements.SETTINGS_CAR_CONFIGURATOR_TAB_BUTTON: pages_dict[Elements.SETTINGS_PAGE_CAR_CONFIGURATOR],
        #    #Elements.SETTINGS_FIGURE_PRINTER_TAB_BUTTON: pages_dict[Elements.SETTINGS_PAGE_FIGURE_PRINTER]
        #}

        self.tabs = [*self.tabs_to_pages.keys()]
        #self.tabs = [
        #    Elements.SETTINGS_TEXT_PRINTER_TAB_BUTTON,
        #    Elements.SETTINGS_CALCULATOR_TAB_BUTTON,
        #    Elements.SETTINGS_CAR_CONFIGURATOR_TAB_BUTTON,
        #    Elements.SETTINGS_FIGURE_PRINTER_TAB_BUTTON
        #]
        self.tabs_bb:BoundingBox = self.get_tabs_bb(self.tabs)
        self.page_area = Elements.SETTINGS_PAGE_AREA

        # self.get_state()[0] represents the opened-state of the settings window
        self.tabs_to_state_index = {button: i+1 for i, button in enumerate(self.tabs)}
        self.close_button = Elements.SETTINGS_CLOSE_BUTTON

        assert len(self.tabs_to_state_index) + 1 == len(self.get_state()) # +1 for opened-state
        self.current_tab:Elements = Elements.SETTINGS_TEXT_PRINTER_TAB_BUTTON
        self.get_state()[1] = 1
        print("initial settings state: ", self.get_state())

    def get_tabs_bb(self, tab_buttons:List[Elements]) -> BoundingBox:
        min_x = inf
        min_y = inf
        width = 0
        height = 0
        for button in tab_buttons:
            if button.bounding_box.x < min_x:
                min_x = button.bounding_box.x
            if button.bounding_box.y < min_y:
                min_y = button.bounding_box.y
            width += button.bounding_box.width
            height += button.bounding_box.height
        return BoundingBox(min_x, min_y, width, height)


    def handle_click(self, click_coordinates:np.ndarray):
        assert self.is_opened() == 1
        if self.close_button.bounding_box.is_point_inside(click_coordinates):
            self.set_opened(0)
        elif self.tabs_bb.is_point_inside(click_coordinates):
            print("click in settings menu!")
            for tab in self.tabs:
                if tab.bounding_box.is_point_inside(click_coordinates):
                    self.set_current_tab(tab)
                    return
        elif self.page_area.bounding_box.is_point_inside(click_coordinates):
            # TODO: traverse all widgets of current page/tab and check if
            #       any are hit by click, then call step() method of widget
            for widget in self.tabs_to_pages[self.current_tab]:
                if widget.get_bounding_box().is_point_inside(click_coordinates):
                    widget.handle_click(click_coordinates)
            pass
        else: 
            pass # no widget clicked


    def set_current_tab(self, current_tab:Elements):
        for tab, index in self.tabs_to_state_index.items():
            if tab == current_tab:
                self.get_state()[index] = 1
                self.current_tab = current_tab
            else:
                self.get_state()[index] = 0


    def is_opened(self) -> int:
        return self.get_state()[0]

    def set_opened(self, opened:int):
        self.get_state()[0] = opened

    def get_current_img_name(self) -> str:
        return self.current_tab.img_name
