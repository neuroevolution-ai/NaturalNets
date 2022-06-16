import numpy as np

from naturalnets.environments.app.state_manipulator import StateManipulator
from naturalnets.environments.app.widget import Widget

class CheckBox(Widget):

    STATE_LEN = 1

    def __init__(self, state_sector, bounding_box):
        super().__init__(state_sector, bounding_box)

    def handle_click(self, click_coordinates:np.ndarray):
        if self.get_state()[0] == 0:
            self.get_state()[0] = 1
        else:
            self.get_state()[0] = 0

    def draw(self, img):
        if self.get_state()[0] == 1:
            #TODO draw cross on own position in img
            pass




