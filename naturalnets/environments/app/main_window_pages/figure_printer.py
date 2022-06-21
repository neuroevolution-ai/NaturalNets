import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.settings_window_pages.figure_printer_settings import FigurePrinterSettings

class FigurePrinter(Page):

    STATE_LEN = 5
    IMG_PATH = IMAGES_PATH + "figure_printer.png"

    def __init__(self, figure_printer_settings:FigurePrinterSettings):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        self.settings = figure_printer_settings

    def handle_click(self, click_position: np.ndarray = None):
        assert self.settings.is_figure_printer_activated()
        print("figure_printer click handle called.")
        print("curr figure color", self.settings.get_figure_color())
        print("curr figure", self.settings.get_figures())
        #TODO
