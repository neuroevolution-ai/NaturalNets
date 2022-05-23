import numpy as np

from abc import ABC, abstractmethod

class Widget(ABC):
  @abstractmethod
  def is_interactable(self) -> bool:
    pass

  @abstractmethod
  def handle_input(self, input:np.ndarray, constraints:np.ndarray = None) -> np.ndarray:
    pass

  @abstractmethod
  def check_constraints(self, input:np.ndarray, constraints:np.ndarray = None) -> bool:
    pass

  @abstractmethod
  def get_state(self) -> np.ndarray:
    pass

  @abstractmethod
  def exec_on_next_step(self) -> None:
    pass

  