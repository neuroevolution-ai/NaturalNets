import names as n

from dropdown import Dropdown

WIDGETS_DICT = {
  n.CALC: {
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
      },
      "constraints": {
        n.CALC_OPERAND_ONE_4: ["constraint.mockup"] 
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
      },
    }
  },
}