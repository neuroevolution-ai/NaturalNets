import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem

class CarConfigurator(Page):

    STATE_LEN = 5
    IMG_PATH = IMAGES_PATH + "car_configurator.png"

    CAR_DROPDOWN_BB = BoundingBox(252, 108, 166, 22)
    TIRE_DROPDOWN_BB = BoundingBox(252, 189, 166, 22)
    INTERIOR_DROPDOWN_BB = BoundingBox(252, 270, 166, 22)
    PROPULSION_DROPDOWN_BB = BoundingBox(252, 351, 166, 22)

    def __init__(self):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        self.car_a_ddi = DropdownItem("Car A")
        self.car_b_ddi = DropdownItem("Car B")
        self.car_c_ddi = DropdownItem("Car C")
        self.car_dropdown = Dropdown(self.CAR_DROPDOWN_BB, [self.car_a_ddi, self.car_b_ddi, self.car_c_ddi])
        pass

    def handle_click(self, click_position: np.ndarray):
        #print("car_configurator click handle called.")
        #TODO
        pass

    def reset(self):
        # close all dropdowns except the car-dropdown
        # select first item in car-dropdown, if any
        pass
