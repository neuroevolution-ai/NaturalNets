import numpy as np
#from numpy.typing import NDArray
import typing

CALCULATOR_BASE_SETTINGS = ["base10", "base2", "base16"]
CALCULATOR_DROPDOWN_SETTINGS = ["addition", "subtraction", "multiplication", "division"]

class CalculatorSettings:

  def __init__(self):
    # calculator settings
    self.calculator_settings_h = ["calc_dropdown", *CALCULATOR_DROPDOWN_SETTINGS, *CALCULATOR_BASE_SETTINGS]
    self.calculator_settings:np.ndarray = np.zeros(len(self.calculator_settings_h), dtype=int)

    self.complete_vector:np.ndarray = np.array([*self.calculator_settings], dtype=int)

  def update(self, vector:np.ndarray):
    self.complete_vector = vector
