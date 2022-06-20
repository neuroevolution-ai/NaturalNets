import cv2
import numpy as np

from typing import List
from abc import ABC, abstractmethod
from naturalnets.environments.app.bounding_box import BoundingBox

class Clickable(ABC):
    @abstractmethod
    def get_bb(self) -> BoundingBox:
        pass

    @abstractmethod
    def handle_click(self, click_position:np.ndarray=None):
        pass

    def is_clicked_by(self, click_position:np.ndarray) -> bool:
        return self.get_bb().is_point_inside(click_position)

class Renderable(ABC):
    @abstractmethod
    def render(self, img:np.ndarray) -> np.ndarray:
        pass