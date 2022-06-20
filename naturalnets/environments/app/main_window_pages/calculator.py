import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.page import Page

class Calculator(Page):

    STATE_LEN = 5
    IMG_PATH = IMAGES_PATH + "calculator.png"

    def __init__(self):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        pass

    def handle_click(self, click_position: np.ndarray = None):
        print("calculator click handle called.")
        #TODO
        pass

