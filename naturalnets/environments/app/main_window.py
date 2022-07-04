import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.constants import IMAGES_PATH
from naturalnets.environments.app.interfaces import Clickable
from naturalnets.environments.app.main_window_pages.calculator import Calculator
from naturalnets.environments.app.main_window_pages.car_configurator import CarConfigurator
from naturalnets.environments.app.main_window_pages.figure_printer import FigurePrinter
from naturalnets.environments.app.main_window_pages.text_printer import TextPrinter
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.utils import render_onto_bb
from naturalnets.environments.app.state_element import StateElement


class MainWindow(StateElement, Clickable):

    STATE_LEN = 4
    IMG_PATH = IMAGES_PATH + "main_window_base.png"
    FIGURE_PRINTER_BUTTON_IMG_PATH = IMAGES_PATH + "figure_printer_button.png"
    BOUNDING_BOX = BoundingBox(0, 0, 448, 448)
    #TODO: change BB of menu area to exclude settings button 
    MENU_AREA_BB = BoundingBox(0, 0, 116, 448)
    PAGES_AREA_BB = BoundingBox(117, 22, 326, 420)

    #SETTINGS_BUTTON_BB = BoundingBox(8, 0, 49, 18)
    TEXT_PRINTER_BUTTON_BB = BoundingBox(9, 28, 99, 22)
    CALCULATOR_BUTTON_BB = BoundingBox(9, 56, 99, 22)
    CAR_CONFIGURATOR_BUTTON_BB =  BoundingBox(9, 84, 99, 22)
    FIGURE_PRINTER_BUTTON_BB = BoundingBox(9, 112, 99, 22)

    def __init__(self):
        super().__init__(self.STATE_LEN)
        self._bounding_box = self.BOUNDING_BOX

        #self.settings_window = SettingsWindow()

        self.text_printer = TextPrinter()
        self.calculator = Calculator()
        self.car_configurator = CarConfigurator()
        self.figure_printer = FigurePrinter()

        self.pages:list[Page] = [self.text_printer, self.calculator, self.car_configurator, self.figure_printer]
        assert len(self.pages) == self.get_state_len()
        self.pages_to_state_index:dict[Page, int] = {page: index for index, page in enumerate(self.pages)}

        self.set_current_page(self.text_printer)

        self.is_figure_printer_button_visible = 0
        self.figure_printer_button = Button(self.FIGURE_PRINTER_BUTTON_BB, lambda: self.set_current_page(self.figure_printer))
        self.buttons = [
            #self.settings_button,
            #Button(self.SETTINGS_BUTTON_BB, lambda: self.settings_window.open()),
            Button(self.TEXT_PRINTER_BUTTON_BB, lambda: self.set_current_page(self.text_printer)),
            Button(self.CALCULATOR_BUTTON_BB, lambda: self.set_current_page(self.calculator)),
            Button(self.CAR_CONFIGURATOR_BUTTON_BB, lambda: self.set_current_page(self.car_configurator)),
            self.figure_printer_button,
        ]

        self.add_children([self.car_configurator, self.figure_printer])
        #self.add_child(self.settings_window)

    def set_figure_printer_button_visible(self, visible:bool) -> None:
        self.is_figure_printer_button_visible = visible

    def get_current_page(self):
        return self.current_page

    def set_current_page(self, current_page:Page):
        for page, index in self.pages_to_state_index.items():
            if page == current_page:
                self.get_state()[index] = 1
                self.current_page = page
            else:
                self.get_state()[index] = 0

    def handle_click(self, click_position:np.ndarray) -> None:

        if self.current_page.is_dropdown_open() or self.PAGES_AREA_BB.is_point_inside(click_position):
            self.current_page.handle_click(click_position)

        elif self.MENU_AREA_BB.is_point_inside(click_position):
            self.handle_menu_click(click_position)

        else:
            # no interactable part of window clicked
            pass

        ## handle state changes resulting from settings state changes

        # switch to text printer if figure printer is current page but not activated in settings
        #if self.current_page == self.figure_printer and not self.is_figure_printer_button_visible():
        #    self.set_current_page(self.text_printer)

    def is_dropdown_open(self):
        return self.current_page.is_dropdown_open()
    
    def handle_menu_click(self, click_position:np.ndarray) -> None:
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                # check if figure printer button is visible
                if not button == self.figure_printer_button or self.is_figure_printer_button_visible:
                    button.handle_click()
                    break

    def render(self, img:np.ndarray):
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.get_bb(), to_render)
        img = self.current_page.render(img)

        if self.is_figure_printer_button_visible:
            figure_printer_img = cv2.imread(self.FIGURE_PRINTER_BUTTON_IMG_PATH)
            img = render_onto_bb(img, self.FIGURE_PRINTER_BUTTON_BB, figure_printer_img)

        #if self.settings_window.is_open():
        #    img = self.settings_window.render(img)

        return img

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self.bounding_box = bounding_box

