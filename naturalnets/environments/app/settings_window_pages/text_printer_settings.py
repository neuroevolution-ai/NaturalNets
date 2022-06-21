import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.interfaces import HasPopups
from naturalnets.environments.app.page import Page

class TextPrinterSettings(Page, HasPopups):
    STATE_LEN = 2
    IMG_PATH = IMAGES_PATH + "text_printer_settings.png"

    def __init__(self):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        pass

    def handle_click(self, click_position: np.ndarray = None):
        print("text_printer_settings click handle called.")
        #TODO
        pass

    def is_popup_open(self) -> bool:
        #TODO
        return False