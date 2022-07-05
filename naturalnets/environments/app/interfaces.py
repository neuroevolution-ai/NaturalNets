import cv2
import numpy as np

from typing import List
from abc import ABC, abstractmethod
from naturalnets.environments.app.bounding_box import BoundingBox


class Renderable(ABC):
    @abstractmethod
    def render(self, img:np.ndarray) -> np.ndarray:
        pass

class HasBoundingBox(ABC):
    @abstractmethod
    def get_bb(self) -> BoundingBox:
        pass

    @abstractmethod
    def set_bb(self, bounding_box:BoundingBox) -> None:
        pass


class Clickable(HasBoundingBox):
    @abstractmethod
    def handle_click(self, click_position:np.ndarray=None) -> None:
        pass

    def is_clicked_by(self, click_position:np.ndarray) -> bool:
        return self.get_bb().is_point_inside(click_position)

class HasPopups(ABC):
    @abstractmethod
    def is_popup_open(self) -> bool:
        pass
