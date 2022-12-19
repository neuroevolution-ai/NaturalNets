
from typing import Callable
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Widget


class Slider(Widget):

    STATE_LEN = 0

    def __init__(self, bounding_box: BoundingBox, states):
        """
        Args:
            
        """
        super().__init__(self.STATE_LEN, bounding_box)

        self.STATE_LEN = states

    def render():
        pass
    