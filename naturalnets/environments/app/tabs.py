import numpy as np
import names as n

from widget import Widget_old
from typing import Dict

class Tabs(Widget_old):

  def __init__(self, tabs:Dict[str, int], constraints:Dict[str,str]=None):
    self._state_len = len(tabs)
    self._state = np.array(list(tabs.values()), dtype=int)

    if np.sum(self._state) != 1:
      raise ValueError("At least one tab has to be selected on tabs initialization.")

    #TODO: maybe put in Widget class (dropdown and this have same functionality)
    self.is_item_constrained_arr = []
    if constraints != None:
      self.is_item_constrained_arr:np.ndarray = np.array([True if key in constraints else False for key in tabs.keys()], dtype=bool)
    
    self.state_h = tabs

  def _validate_input(self, input:np.ndarray) -> None:
    #TODO
    pass
  
  def _validate_constraints(self, input:np.ndarray, constraint_state:np.ndarray = None) -> None:
    #TODO
    pass

  def _mutate_state(self, input:np.ndarray) -> None:
    #TODO
    pass

  #TODO: maybe put in Widget class
  def get_state(self):
    return self._state

  #TODO: can probably be part of abstract class (at least tabs and dropdown share the same impl)
  def get_state_h(self):
    i = 0
    for key in self.state_h:
      self.state_h[key] = self._state[i]
      i = i+1
    return self.state_h



