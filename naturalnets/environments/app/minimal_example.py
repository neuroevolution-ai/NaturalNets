import numpy as np
import names as n
import time

from typing import Dict, List
from widget import Widget
from dropdown import Dropdown


TEST_WIDGETS = {
  n.CALC_OPERAND_ONE_DROPDOWN: {
    "state_len": 6,
    "type": Dropdown,
    "args": {
      "name": n.CALC_OPERAND_ONE_DROPDOWN,
      "items": [
        n.CALC_OPERAND_ONE_0,
        n.CALC_OPERAND_ONE_1,
        n.CALC_OPERAND_ONE_2,
        n.CALC_OPERAND_ONE_3,
        n.CALC_OPERAND_ONE_4,
      ]
    }
  },
  n.CALC_OPERAND_TWO_DROPDOWN: {
    "state_len": 6,
    "type": Dropdown,
    "args": {
      "name": n.CALC_OPERAND_TWO_DROPDOWN,
      "items": [
        n.CALC_OPERAND_TWO_0,
        n.CALC_OPERAND_TWO_1,
        n.CALC_OPERAND_TWO_2,
        n.CALC_OPERAND_TWO_3,
        n.CALC_OPERAND_TWO_4,
      ]
    }
  }
}

class App:
  def __init__(self):
    self._state_len = 0
    self._state = np.array([],dtype=int)
    self._name_to_index:dict[str,int] = {}
    self._add_elements_to_state({"padding.1": 0, "padding.2": 1})


    self.page = Page(TEST_WIDGETS)
    np.append(self._state,self.page.get_state())
    np.append(self._state, [1,0])
    print("initial state: ", self._state)

  def _add_elements_to_state(self, name_to_state:Dict[str,int]) -> None:
    for (name, state) in name_to_state.items():
      self._name_to_index[name] = len(self._state)
      np.append(self._state, state)

  def step(self, action:np.ndarray):
    print("action: ", action[:6])
    self.page.step(n.CALC_OPERAND_ONE_DROPDOWN, action[:6])
    print("app state: ", self._state)
    print("page state: ", self.page.get_state())
    pass

class Page:
  def __init__(self, widgets:Dict[str,Widget]):
    self._widgets:dict[str,Widget] = {k: v["type"](**v["args"]) for (k,v) in widgets.items()}

  def step(self, widget_name:str, input:np.ndarray, constraint_state:np.ndarray=None):
    self._widgets[widget_name].step(input, constraint_state)
    self.act(widget_name)
    pass

  def act(self, widget_name):
    #TODO: some functionality on state, e.g. for calculator: calculating
    # only if widget would trigger action
    pass

  def get_state(self):
    print([widget.get_state() for widget in self._widgets.values()])
    return np.concatenate([widget.get_state() for widget in self._widgets.values()])
    #return np.array([element for widget in self._widgets.values() for element in widget.get_state()], dtype=int)
  
  def get_state_h(self) -> Dict[str, int]:
    d = {}
    for widget in self._widgets.values():
      d.update(widget.get_state_h())
    print(d)
    return d


if __name__=="__main__":
  app = App()
  app.step(np.array([1,1,0,0,0,0,0,1,0,0,0,0], dtype=int))






