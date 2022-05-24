from dropdown import Dropdown
import numpy as np
import names as n

CALCULATOR_WIDGETS = {
  n.CALC_OPERAND_ONE_DROPDOWN: {
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
  },
  n.CALC_OPERATOR_DROPDOWN: {
    "type": Dropdown,
    "args": {
      "name": n.CALC_OPERATOR_DROPDOWN,
      "items": [
        n.CALC_OPERATOR_ADD,
        n.CALC_OPERATOR_SUB,
        n.CALC_OPERATOR_MULT,
        n.CALC_OPERATOR_DIV
      ],
      "constraints": {
        n.CALC_OPERATOR_ADD: n.SETTINGS_CALC_ADD,
        n.CALC_OPERATOR_SUB: n.SETTINGS_CALC_SUB,
        n.CALC_OPERATOR_MULT: n.SETTINGS_CALC_MULT,
        n.CALC_OPERATOR_DIV: n.SETTINGS_CALC_DIV
      }
    }
  },
  # result encoded binary: [0,1,0,0,0] = 16, 
  # binary 17, 18, 19, 20 are used to represent the possible
  # negative numbers -1, -2, -3, -4 respectively.
  # All other values are invalid
  n.CALCULATOR_RESULT: {
    "init_value": np.zeros(5, dtype=int)  
  },
  n.CALCULATOR_BUTTON: {
    "init_value": 0
  }
}