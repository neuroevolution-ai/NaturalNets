import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.page import Page

class CarConfiguratorSettings(Page):
    STATE_LEN = 2
    IMG_PATH = IMAGES_PATH + "car_configurator_settings.png"

    def __init__(self):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        pass

    def handle_click(self, click_position: np.ndarray = None):
        print("car_configurator_settings click handle called.")
        #TODO
        pass