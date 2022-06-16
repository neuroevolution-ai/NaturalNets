import numpy as np
import naturalnets.environments.app.names as n

from naturalnets.environments.app.dropdown import Dropdown
from naturalnets.environments.app.widget import Widget_old
from typing import Dict

POSSIBLE_OPERANDS_BASE_10 = [i for i in range(5)]  # pragma: no cover
POSSIBLE_OPERANDS_BASE_2 = [bin(i) for i in range(5)]  # pragma: no cover
POSSIBLE_OPERANDS_BASE_16 = [hex(i) for i in range(5)]  # pragma: no cover

NUMERAL_SYSTEMS = ["Base 10", "Base 2", "Base 16"]  # pragma: no cover

FIRST_OPERAND_DROPDOWN_NAME = "first_operand"
SECOND_OPERAND_DROPDOWN_NAME = "second_operand"
OPERAND_DROPDOWN_OPTIONS = ["0", "1", "2", "3", "4"]

#INITIAL_CALCULATOR_VECTOR = [(0)]

#TODO: add result widget
# think about interactable state elements and non interactable state elements 
#    - e.g. calculator result is non-interactable
#    -> non-interactable state could probably be part of the page instead of its
#       own widget
WIDGETS = [n.CALC_OPERAND_ONE_DROPDOWN, n.CALC_OPERAND_TWO_DROPDOWN, n.CALC_OPERATOR_DROPDOWN]


class Calculator:
    def __init__(self, state_sector:np.ndarray, widgets:Dict[str,Widget_old]):  # pragma: no cover

        self.operand_one_dropdown:Dropdown = widgets[n.CALC_OPERAND_ONE_DROPDOWN]
        self.operand_two_dropdown:Dropdown = widgets[n.CALC_OPERAND_TWO_DROPDOWN]
        self.operator_dropdown:Dropdown = widgets[n.CALC_OPERATOR_DROPDOWN]
        self._result:np.ndarray = state_sector

        self.numeral_system:str = "Base 10" #TODO: should come from settings

        #self.signal_handler = SignalHandler()

    def step(self):
        operand_one:int = self.operand_one_dropdown.get_current_value()
        operand_two:int = self.operand_two_dropdown.get_current_value()
        operator:str = self.operator_dropdown.get_current_value()

        result = 0
        if operator == "+":
            result = operand_one + operand_two
        elif operator == "-":
            result = operand_one - operand_two
        elif operator == "*":
            result = operand_one * operand_two
        elif operator == "/":
            result = operand_one / operand_two
        else:
            raise ValueError("Unknown operand type.")

        print("Calculator result:", result)
