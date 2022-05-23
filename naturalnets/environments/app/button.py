import numpy as np

from widget import Widget
from typing import Dict

class Button(Widget):

  def __init__(self, name:str):
    self.name = name
    self.state = 0

  #def is_interactable(self) -> bool:
  #  return True

  def handle_input(self, input:np.ndarray, constraints:np.ndarray = None) -> np.ndarray:
    assert len(input) == 1
    assert input[0] == 1
    self.state = 1
    return np.array(self.state, dtype=int)

  def exec_on_next_step(self) -> None:
    if self.state == 1:
      self.state == 0

  def _validate_constraints(self, input:np.ndarray, constraints:np.ndarray = None) -> bool:
    # irrelevant for button
    #TODO: don't use in Widget interface?
    pass

  def get_state(self) -> np.ndarray:
    return np.array(self.state, dtype=int)

  def get_state_h(self) -> Dict[str,int]:
    return {self.name: self.state}
