"""Contains interfaces/abstract classes."""
from abc import ABC, abstractmethod

import numpy as np
from naturalnets.environments.app.bounding_box import BoundingBox

class Renderable(ABC):
    """Represents a Renderable."""
    @abstractmethod
    def render(self, img:np.ndarray) -> np.ndarray:
        """Renders this Renderable onto the given cv2 image."""

class HasBoundingBox(ABC):
    """Represents an element with a BoundingBox."""
    @abstractmethod
    def get_bb(self) -> BoundingBox:
        """Returns this elements' bounding box."""

    @abstractmethod
    def set_bb(self, bounding_box:BoundingBox) -> None:
        """Sets this elements' bounding box."""


class Clickable(HasBoundingBox):
    """Represents a element that can be clicked."""
    @abstractmethod
    def handle_click(self, click_position:np.ndarray) -> None:
        """This elements' on-click action."""

    def is_clicked_by(self, click_position:np.ndarray) -> bool:
        """Returns true if the given click-position is inside of this elements'
        bounding box."""
        return self.get_bb().is_point_inside(click_position)

class HasPopups(ABC):
    """Represents an element which has at least one popup."""
    @abstractmethod
    def is_popup_open(self) -> bool:
        """Returns true if any popup is open."""
