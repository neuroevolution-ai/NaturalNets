"""Contains interfaces/abstract classes."""
from abc import ABC, abstractmethod
from typing import Optional, Tuple

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox


class Renderable(ABC):
    """Represents a Renderable."""

    @abstractmethod
    def render(self, img: np.ndarray) -> np.ndarray:
        """Renders this Renderable onto the given cv2 image."""


class HasBoundingBox(ABC):
    """Represents an element with a BoundingBox."""

    @abstractmethod
    def get_bb(self) -> BoundingBox:
        """Returns this elements' bounding box."""

    @abstractmethod
    def set_bb(self, bounding_box: BoundingBox) -> None:
        """Sets this elements' bounding box."""
        pass


class Clickable(HasBoundingBox):
    """Represents an element that can be clicked."""

    @abstractmethod
    def handle_click(self, click_position: np.ndarray) -> None:
        """The on-click action of this element."""
        pass

    def calculate_distance_to_click(self, click_position: np.ndarray, current_minimal_distance: Optional[float],
                                    current_clickable: Optional["Clickable"]) -> Tuple[float, "Clickable"]:
        own_distance = self.get_bb().distance_to_point(click_position)

        if own_distance < current_minimal_distance:
            return own_distance, self

        return current_minimal_distance, current_clickable

    def is_clicked_by(self, click_position: np.ndarray) -> bool:
        """Returns true if the given click-position is inside this elements'
        bounding box."""
        return self.get_bb().is_point_inside(click_position)


class HasPopups(ABC):
    """Represents an element which has at least one popup."""

    @abstractmethod
    def is_popup_open(self) -> int:
        """Returns true if any popup is open."""
        pass
