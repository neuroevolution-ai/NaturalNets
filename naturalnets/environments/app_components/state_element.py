from abc import abstractmethod
from typing import List

import numpy as np

from naturalnets.environments.gui_app.exception import ArgumentError
from naturalnets.environments.app_components.interfaces import Renderable


class StateElement(Renderable):
    """Basic building block of the app. Represents the elements (in {0, 1})
    in the app's state vector.
    A StateElement may have children StateElements, which allows recursively traversing all
    state-elements in order to get the app's total state vector length, as well as assign
    part of the app's total state vector to every StateElement. Each StateElement then manipulates
    its part of the app's total state vector directly, in order to save computation time."""

    def __init__(self, state_len: int):
        self._state_len = state_len
        self._state: np.ndarray = np.zeros(state_len, dtype=int)
        self._children: List['StateElement'] = []

    def get_state(self) -> np.ndarray:
        """Returns this state's current state."""
        return self._state

    def get_state_len(self) -> int:
        """Returns the state length of this state-element."""
        return self._state_len

    def assign_state_sector(self, state_sector: np.ndarray):
        """Will assign the given state-sector to this state-element. This means
        the given state-sector will be mutated according to this state-elements current
        state and future state changes!
        Can't be used to set this element's state.

        Args:
            state_sector (np.ndarray): the state-sector to be assigned to this element.
            Needs to be a zero-vector!

        Raises:
            ArgumentError: if the state-sector is a non-zero vector.
        """
        if np.count_nonzero(state_sector) > 0:
            # throw error to emphasize that state_sector state would be overwritten
            # i.e. state cannot be set with this method
            raise ArgumentError("Given state sector is not empty.")

        if len(state_sector) != self.get_state_len():
            raise ArgumentError(f"Given state sector length ({len(state_sector)}) does not "
                                f"match state element state length ({self._state_len}).")

        current_state = np.copy(self.get_state())
        self._state = state_sector
        self._state[:] = current_state[:]

    def get_children(self) -> List['StateElement']:
        """Returns all children of this StateElement."""
        return self._children

    def add_child(self, child: 'StateElement'):
        """Adds a child to this StateElement."""
        self.get_children().append(child)

    def add_children(self, children: List['StateElement']):
        """Adds all given children to this StateElement."""
        for child in children:
            self.add_child(child)

    @abstractmethod
    def render(self, img: np.ndarray) -> np.ndarray:
        pass
