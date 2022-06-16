import numpy as np

from abc import ABC, abstractmethod
from typing import Dict

from naturalnets.environments.app.exception import ArgumentError

class StateManipulator(ABC):

  def __init__(self, state_sector:np.ndarray):
    for element in state_sector:
      if element != 0:
        raise ArgumentError("Attempting to initialize StateManipulator, but given state_sector is not empty.")

    self._state = state_sector

  def get_state(self):
    return self._state

  @abstractmethod
  def handle_click(self, click_coordinates:np.ndarray) -> np.ndarray:
    pass

