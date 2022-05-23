import numpy as np

from abc import ABC, abstractmethod
from typing import Dict

class Widget(ABC):
  #@abstractmethod
  #def is_interactable(self) -> bool:
  #  pass
  def step(self, input:np.ndarray, constraint_state:np.ndarray = None) -> np.ndarray:
    self._validate_input(input)
    self._validate_constraints(input, constraint_state)
    self._mutate_state(input)
    return self.get_state()

  @abstractmethod
  def _validate_input(self, input:np.ndarray) -> None:
    pass
  
  @abstractmethod
  def _validate_constraints(self, input:np.ndarray, constraint_state:np.ndarray = None) -> None:
    pass

  @abstractmethod
  def _mutate_state(self, input:np.ndarray) -> None:
    pass

  @abstractmethod
  def get_state(self):
    pass

  @abstractmethod
  def exec_on_next_step(self) -> None:
    pass
  