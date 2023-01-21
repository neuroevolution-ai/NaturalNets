
from typing import Callable

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Widget


class Slider(Widget):

    STATE_LEN = 0

    def __init__(self, bounding_box: BoundingBox, states, action: Callable = None):
        """
        Args:
            
        """
        self.STATE_LEN = states
        self.action = action
        super().__init__(self.STATE_LEN, bounding_box)


    def render():
        pass

    def handle_click(self, click_position: np.ndarray = None) -> None:
        if(self.has_click_action()):
            self.action()
        
        self._state = np.roll(self.get_state(), 1)
        
    def has_click_action(self): 
        if self.action is not None:
            return True
    
    def set_slider_value(self, state):
        self.get_state()[state] = 1
    
    def get_slider_value(self):
        return np.argmax(self.get_state())
    
    
    