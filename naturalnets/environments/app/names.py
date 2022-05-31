from dropdown import Dropdown

##### how to #######
# - each name must be unique
# - each element in the state vector must have a name
# - constraints are also elements of the state vector (must have a name)
#   e.g.: CALC_OPERATOR_DIV has constraint SETTINGS_CALC_DIV
# - each name represents exactly one element in the state vector
#######################

# TODO: enums verwenden

## 1. general ##

# 1.1 pages
SETTINGS = "settings"
TEXT_PRINTER = "text_printer"
CALC = "calculator"
CAR_CONFIG = "car_config"

# 1.2 text printer
TEXT_PRINTER_PRINT_TEXT = "text_printer.print_text" # TODO: widget(Button) of text printer


# 1.2 calculator

CALC_OPERAND_ONE_DROPDOWN = "calc.opreand_one_dropdown"
CALC_OPERAND_ONE_0 = "calc.opreand_one.0"
CALC_OPERAND_ONE_1 = "calc.opreand_one.1"
CALC_OPERAND_ONE_2 = "calc.opreand_one.2"
CALC_OPERAND_ONE_3 = "calc.opreand_one.3"
CALC_OPERAND_ONE_4 = "calc.opreand_one.4"

CALC_OPERAND_TWO_DROPDOWN = "calc.opreand_two_dropdown"
CALC_OPERAND_TWO_0 = "calc.opreand_two.0"
CALC_OPERAND_TWO_1 = "calc.opreand_two.1"
CALC_OPERAND_TWO_2 = "calc.opreand_two.2"
CALC_OPERAND_TWO_3 = "calc.opreand_two.3"
CALC_OPERAND_TWO_4 = "calc.opreand_two.4"

CALC_OPERATOR_DROPDOWN = "calc.operator"
CALC_OPERATOR_ADD = "calc.operator.add"
CALC_OPERATOR_SUB = "calc.operator.sub"
CALC_OPERATOR_MULT = "calc.operator.mult"
CALC_OPERATOR_DIV = "calc.operator.div"

CALCULATOR_RESULT = "calc.result"
CALCULATOR_BUTTON = "calc.button"

## 2. settings ##

# 2.1 general
SETTINGS_TABS_TEXT_PRINTER = "settings.tabs.text_printer"
SETTINGS_TABS_CALCULATOR = "settings.tabs.calculator"
SETTINGS_TABS_CAR_CONFIG = "settings.tabs.car_config"
SETTINGS_TABS_FIGURE_PRINTER = "settings.tabs.figure_printer"

SETTINGS_CLOSE = "settings.close"

# 2.2 calculator
SETTINGS_CALC_ADD = "settings.calc.add"
SETTINGS_CALC_SUB = "settings.calc.sub"
SETTINGS_CALC_MULT = "settings.calc.mult"
SETTINGS_CALC_DIV = "settings.calc.div"

SETTINGS_CALC_BASE_DROPDOWN = "settings.calc.base_dropdown"
SETTINGS_CALC_BASE_2 = "settings.calc.base.2"
SETTINGS_CALC_BASE_10 = "settings.calc.base.10"
SETTINGS_CALC_BASE_16 = "settings.calc.base.16"