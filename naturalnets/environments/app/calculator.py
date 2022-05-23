import numpy as np
from dropdown import Dropdown
import names


POSSIBLE_OPERANDS_BASE_10 = [i for i in range(5)]  # pragma: no cover
POSSIBLE_OPERANDS_BASE_2 = [bin(i) for i in range(5)]  # pragma: no cover
POSSIBLE_OPERANDS_BASE_16 = [hex(i) for i in range(5)]  # pragma: no cover

NUMERAL_SYSTEMS = ["Base 10", "Base 2", "Base 16"]  # pragma: no cover

FIRST_OPERAND_DROPDOWN_NAME = "first_operand"
SECOND_OPERAND_DROPDOWN_NAME = "second_operand"
OPERAND_DROPDOWN_OPTIONS = ["0", "1", "2", "3", "4"]

#INITIAL_CALCULATOR_VECTOR = [(0)]



class Calculator:
    def __init__(self):  # pragma: no cover


        self.calculator_output = 0 #TODO
        self.first_operand_combobox:Dropdown = Dropdown(FIRST_OPERAND_DROPDOWN_NAME, OPERAND_DROPDOWN_OPTIONS)
        self.second_operand_combobox:Dropdown = Dropdown(SECOND_OPERAND_DROPDOWN_NAME, OPERAND_DROPDOWN_OPTIONS)
        self.math_operator_combobox:Dropdown = Dropdown()
        self.numeral_system = "Base 10"

        self.addition_operator = False
        self.subtraction_operator = False
        self.multiplication_operator = False
        self.division_operator = False

        self.state:np.ndarray = np.array([
                                         *self.first_operand_combobox.get_state(), 
                                         *self.second_operand_combobox.get_state()
                                         ]
                                         ,dtype=int)
        self.state = np.zeros(10, dtype=int)
        self._initialize()

        #self.signal_handler = SignalHandler()

    def print_state(self):
      print(self.state)

    def get_state(self):
        return self.state

