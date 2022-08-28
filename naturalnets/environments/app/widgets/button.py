from typing import Callable

import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.interfaces import Clickable


class Button(Clickable):
    """Represents a Button with a click-action.
    """

    def __init__(self, bounding_box: BoundingBox, click_action: Callable):
        self._bounding_box = bounding_box
        self._click_action = click_action

    def get_bb(self):
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def handle_click(self, click_position: np.ndarray) -> None:
        self._click_action()
