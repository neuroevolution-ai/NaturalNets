import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.interfaces import HasPopups
from naturalnets.environments.app.main_window_pages.calculator import Calculator
from naturalnets.environments.app.page import Page

class CalculatorSettings(Page):
    STATE_LEN = 5
    IMG_PATH = IMAGES_PATH + "calculator_settings.png"

    def __init__(self, calculator:Calculator):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        self.calculator = calculator
        pass

    def handle_click(self, click_position: np.ndarray = None):
        print("calculator_settings click handle called.")
        #TODO
        pass

    def is_popup_open(self) -> bool:
        #TODO
        return False