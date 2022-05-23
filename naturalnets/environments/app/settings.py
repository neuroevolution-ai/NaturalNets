import numpy as np
import names as n

from typing import Dict
from button import Button
from tabs import Tabs


SETTINGS_WIDGETS_DICT = {
  "tabs": {
    "type": Tabs,
    "args": {
      "tabs": {
        n.SETTINGS_TABS_TEXT_PRINTER: 1,
        n.SETTINGS_TABS_CALCULATOR: 0,
        n.SETTINGS_TABS_CAR_CONFIG: 0,
        n.SETTINGS_TABS_FIGURE_PRINTER: 0
      },
      "constraints": None
    }
  },
  "buttons": {
    n.SETTINGS_CLOSE: {
      "type": Button,
      "args": {
        "name": n.SETTINGS_CLOSE
      }
    }
  }
}

class Settings:
  def __init__(self):
    #self.tabs_h = SETTINGS_WIDGETS_DICT["tabs"]["tabs"]

    #self.current_tab_h:str = None
    #for tab in self.tabs_h:
    #  if self.tabs_h[tab] == 1:
    #    self.current_tab_h = tab

    tabs_dict = SETTINGS_WIDGETS_DICT["tabs"]
    self._tabs:Tabs = tabs_dict["type"](**tabs_dict["args"])

    button_dict = SETTINGS_WIDGETS_DICT[n.SETTINGS_CLOSE]
    self._close_button:Button = button_dict["type"](**button_dict["args"])

    self._state_len = len(SETTINGS_WIDGETS_DICT["tabs"]) + len(SETTINGS_WIDGETS_DICT["buttons"])
    self._state = np.array([*self._tabs.get_state(), *self._close_button.get_state()], dtype=int)

    self._widgets = [self._tabs, self._close_button]


  def step(self, input:np.ndarray,):
    for widget in self._widgets:
      widget.step()




class CalculatorSettings:

  def __init__(self):
    # calculator settings
    self.calculator_settings_h = ["calc_dropdown", *CALCULATOR_DROPDOWN_SETTINGS, *CALCULATOR_BASE_SETTINGS]
    self.calculator_settings:np.ndarray = np.zeros(len(self.calculator_settings_h), dtype=int)

    self.complete_vector:np.ndarray = np.array([*self.calculator_settings], dtype=int)

  def update(self, vector:np.ndarray):
    self.complete_vector = vector
