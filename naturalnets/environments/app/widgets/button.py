import numpy as np

from typing import Callable
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.interfaces import Clickable

#TODO: button is strictly not a widget since it has no state/is no StateElement
class Button(Clickable):
    def __init__(self, bounding_box:BoundingBox, click_action:Callable):
        self._bounding_box = bounding_box
        self._click_action = click_action

    def get_bb(self):
        return self._bounding_box
        
    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def handle_click(self, click_position: np.ndarray = None) -> None:
        self._click_action()