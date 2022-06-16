from naturalnets.environments.app.check_box import CheckBox
from naturalnets.environments.app.main_window import MainWindow
import naturalnets.environments.app.names as n

from naturalnets.environments.app.dropdown import Dropdown
from naturalnets.environments.app.calculator import Calculator
from naturalnets.environments.app.elements import Elements

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

nav_element_to_img_name = {
  Elements.TEXT_PRINTER_BUTTON: "text_printer",
  Elements.CALCULATOR_BUTTON: "calculator",
  Elements.CAR_CONFIGURATOR_BUTTON: "car_configurator",
  Elements.FIGURE_PRINTER_BUTTON: "figure_printer",

  Elements.SETTINGS_TEXT_PRINTER_TAB_BUTTON: "settings_text_printer",
  Elements.SETTINGS_CALCULATOR_TAB_BUTTON: "settings_calculator",
  Elements.SETTINGS_CAR_CONFIGURATOR_TAB_BUTTON: "settings_car_configurator",
  Elements.SETTINGS_FIGURE_PRINTER_TAB_BUTTON: "settings_figure_printer",
}

MAIN_WINDOW_PAGES = {

}

SETTINGS_WINDOW_PAGES = {
  # Settings_text-Printer
  Elements.SETTINGS_PAGE_TEXT_PRINTER: {
    "navigator": Elements.SETTINGS_TEXT_PRINTER_TAB_BUTTON,
    "state_len": 0,
    "widgets": [
      {
        "state_len": 1,
        "type": CheckBox,
        "args": {
          "bounding_box": Elements.SETTINGS_TEXT_PRINTER_WIDGET_BOLD.bounding_box
        },
      },
    ]
  },
  Elements.SETTINGS_PAGE_CALCULATOR: {
    "navigator": Elements.SETTINGS_CALCULATOR_TAB_BUTTON,
    "state_len": 0,
    "widgets": [
    ]
  },
  Elements.SETTINGS_PAGE_CAR_CONFIGURATOR: {
    "navigator": Elements.SETTINGS_CAR_CONFIGURATOR_TAB_BUTTON,
    "state_len": 0,
    "widgets": [
    ]
  },
  Elements.SETTINGS_PAGE_FIGURE_PRINTER: {
    "navigator": Elements.SETTINGS_FIGURE_PRINTER_TAB_BUTTON,
    "state_len": 0,
    "widgets": [
    ]
  },
}

WINDOWS_DICT = {
  Elements.MAIN_WINDOW: {
    "state_len": 5,
    "type": MainWindow,
    "buttons": [
      Elements.SETTINGS_BUTTON,
      Elements.TEXT_PRINTER_BUTTON,
      Elements.CALCULATOR_BUTTON,
      Elements.CAR_CONFIGURATOR_BUTTON,
      Elements.FIGURE_PRINTER_BUTTON,
    ],
    "widgets": {
      Elements.SETTINGS_BUTTON,
      Elements.TEXT_PRINTER_BUTTON,
      Elements.CALCULATOR_BUTTON,
      Elements.CAR_CONFIGURATOR_BUTTON,
      Elements.FIGURE_PRINTER_BUTTON,
    },
    "pages": {
      Elements.PAGE_TEXT_PRINTER,
      Elements.PAGE_CALCULATOR,
      Elements.PAGE_CAR_CONFIGURATOR,
      Elements.PAGE_FIGURE_PRINTER
    }
  },
}

WIDGETS_DICT_old = {
  n.CALC: {
    "state_len": 5,
    "type": Calculator,
    # "bounding_box": PAGE_BB,
    "widgets": {
      n.CALC_OPERAND_ONE_DROPDOWN: {
        "state_len": 6,
        "type": Dropdown,
        "args": {
          "name": n.CALC_OPERAND_ONE_DROPDOWN,
          "items_dict": {
            # name: value
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