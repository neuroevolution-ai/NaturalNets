import numpy as np

from abc import ABC, abstractmethod
from typing import Dict

from exception import ArgumentError

class Widget(ABC):

  def __init__(self, state_sector:np.ndarray, name:str):
    for element in state_sector:
      if element != 0:
        raise ArgumentError("Attempting to initialize widget, but given state_sector is not empty.")

    self._state = state_sector
    self._name = name

  def set_state(self, state:np.ndarray):
    if not self._validate_state(state):
      raise ArgumentError("Attempting to set invalid state in widget: " + self._name)
    else:
      self._state[:] = state

  def step(self, input:np.ndarray) -> np.ndarray:
    self._validate_input(input)
    #self._validate_constraints(input, constraint_state)
    self._mutate_state(input)
    return self.get_state()

  def get_state(self):
    return self._state

  def get_name(self):
    return self._name

  @abstractmethod
  def _validate_state(self, state:np.ndarray) -> bool:
    pass

  @abstractmethod
  def get_element_name_to_index(self) -> Dict[str,int]:
    pass

  @abstractmethod
  def _validate_input(self, input:np.ndarray) -> None:
    pass
  
  @abstractmethod
  def _mutate_state(self, input:np.ndarray) -> None:
    pass

  @abstractmethod
  def exec_on_invalid_action(self) -> None:
    pass
  