import names as n

from dropdown import Dropdown
from calculator import Calculator

# structure:
# page_name: {
#   state_len: int
#   type: Page-type
#   widgets: {
#     widget_name {
#       state_len: int
#       type: Widget-subtype
#       args: args-to-instantiate Widget-subtype 
#             (must contain names of all state-elements the widget uses)
#       constraints: constraints for elements of the widget 
#                    (constraints are other elements)
#     }, ...
#   }
# }, ...

WIDGETS_DICT = {
  n.CALC: {
    "state_len": 5,
    "type": Calculator,
    "widgets": {
      n.CALC_OPERAND_ONE_DROPDOWN: {
        "state_len": 6,
        "type": Dropdown,
        "args": {
          "name": n.CALC_OPERAND_ONE_DROPDOWN,
          "items_dict": {
            n.CALC_OPERAND_ONE_0: 0,
            n.CALC_OPERAND_ONE_1: 1,
            n.CALC_OPERAND_ONE_2: 2,
            n.CALC_OPERAND_ONE_3: 3,
            n.CALC_OPERAND_ONE_4: 4,
          }
        },
      },
      n.CALC_OPERAND_TWO_DROPDOWN: {
        "state_len": 6,
        "type": Dropdown,
        "args": {
          "name": n.CALC_OPERAND_TWO_DROPDOWN,
          "items_dict": {
            n.CALC_OPERAND_TWO_0: 0,
            n.CALC_OPERAND_TWO_1: 1,
            n.CALC_OPERAND_TWO_2: 2,
            n.CALC_OPERAND_TWO_3: 3,
            n.CALC_OPERAND_TWO_4: 4,
          }
        },
      },
      n.CALC_OPERATOR_DROPDOWN: {
        "state_len": 5,
        "type": Dropdown,
        "args": {
          "name": n.CALC_OPERATOR_DROPDOWN,
          "items_dict": {
            n.CALC_OPERATOR_ADD: "+",
            n.CALC_OPERATOR_SUB: "-",
            n.CALC_OPERATOR_MULT: "*",
            n.CALC_OPERATOR_DIV: "/"
          },
          # TODO: insert when settings are implemented
          #"constraints": {
          #  n.CALC_OPERATOR_ADD: n.SETTINGS_CALC_ADD,
          #  n.CALC_OPERATOR_SUB: n.SETTINGS_CALC_SUB,
          #  n.CALC_OPERATOR_MULT: n.SETTINGS_CALC_MULT,
          #  n.CALC_OPERATOR_DIV: n.SETTINGS_CALC_DIV
          #}
        }
      },
    }
  }
}