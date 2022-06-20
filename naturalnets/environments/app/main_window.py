import cv2
import numpy as np

from typing import Dict
from naturalnets.environments.app.elements import Elements
from naturalnets.environments.app.settings_window import SettingsWindow
from naturalnets.environments.app.state_manipulator import StateManipulator

class MainWindow(StateManipulator):

    STATE_LEN = 4

    def __init__(self, state_sector:np.ndarray, settings:SettingsWindow):
        super().__init__(state_sector)

        #TODO: field: self._state= state_sector, then map 
        #      pages to indexes of that state sector,
        #      then manipulate state_sector[index] to change overall state sector of app

        self.settings = settings

        self.buttons_to_pages = {
            Elements.TEXT_PRINTER_BUTTON: Elements.PAGE_TEXT_PRINTER, 
            Elements.CALCULATOR_BUTTON: Elements.PAGE_CALCULATOR,
            Elements.CAR_CONFIGURATOR_BUTTON: Elements.PAGE_CAR_CONFIGURATOR,
            Elements.FIGURE_PRINTER_BUTTON: Elements.PAGE_FIGURE_PRINTER,
        }


        pages = [page for page in self.buttons_to_pages.values()]
        assert len(pages) == len(self.get_state())
        self.pages_to_state_index = {page: i for i, page in enumerate(pages)}

        # set initial page
        self.get_state()[self.pages_to_state_index[Elements.PAGE_TEXT_PRINTER]] = 1
        self.current_page = Elements.PAGE_TEXT_PRINTER
        print("main_window state:", self.get_state())
        #self.current_img = self.current_page.img_name + '.png'
  
    def handle_click(self, click_coordinates:np.ndarray) -> str:
        if self.settings.is_opened():
            self.settings.handle_click(click_coordinates)
        elif Elements.MAIN_WINDOW_PAGES.bounding_box.is_point_inside(click_coordinates):
            # TODO
            #self.current_page.step(click_coordinates)
            print("Click in pages area of main window!")
            print("pages not yet implemented!")
            #TODO return page.step(click_coordinates) # should return img_name
        else: # click was in menu
            print("click in menu area of main window!")
            # open settings
            if Elements.SETTINGS_BUTTON.bounding_box.is_point_inside(click_coordinates):
                self.settings.set_opened(1)
                return

            # change main-window page
            for button, page in self.buttons_to_pages.items():
                if button.bounding_box.is_point_inside(click_coordinates):
                    self.set_current_page(page)
                    return

        # click outside of any widget

    def set_current_page(self, current_page):
        for page, index in self.pages_to_state_index.items():
            if page == current_page:
                self.get_state()[index] = 1
                self.current_page = page
            else:
                self.get_state()[index] = 0

    def get_current_img_name(self) -> str:
        img = self.current_page.img_name
        if self.settings.is_opened():
            # TODO: one could have a separate img for each main-window page
            #       s.t. the repective page can be seen behind the settings
            #       window..
            img = "text_printer"
            img = img + "_" + self.settings.get_current_img_name()

        # TODO: draw widget-dependent state (each widget in currrently
        # openende window draws its state, if any), then return img instead
        # of str
        return img + ".png"

    def render(self) -> np.ndarray:
        img = cv2.imread(self.current_page.img_name)
        for widget in current_page.get_widgets():
            widget.render(img)
        if self.settings.is_opened():
            self.settings.render(img)
        return img
