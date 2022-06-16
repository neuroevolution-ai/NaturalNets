from enum import Enum, unique
from naturalnets.environments.app.element_bounding_box import ElementBB
from naturalnets.environments.app.names import SETTINGS

WIDTH = 448
HEIGHT = 448

PAGE_BB = ElementBB(0, 0, WIDTH, HEIGHT)

SETTINGS_PAGE_BB = ElementBB(25,48,378, 262)
# https://docs.python.org/3/library/enum.html

class AutoNumber(Enum):
    def __new__(cls, *args):      # this is the only change from above
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

@unique
class Elements(AutoNumber):

  def __init__(self, bounding_box:ElementBB, img_name:str="none"):
    self.bounding_box = bounding_box
    self.img_name = img_name

  ## Global: Pages, Buttons
  MAIN_WINDOW = ElementBB(0, 0, WIDTH, HEIGHT), "text_printer" # default page is text_printer (page shown on start)
  MAIN_WINDOW_PAGES = ElementBB(115, 19, 448, 448)
  SETTINGS_PAGES = ElementBB(25,48,378, 262) # TODO: needed? may be substituted by SETTINGS_PAGE_...

  SETTINGS_BUTTON = ElementBB(8, 0, 49, 18)
  TEXT_PRINTER_BUTTON = ElementBB(9, 28, 99, 22)
  CALCULATOR_BUTTON = ElementBB(9, 56, 99, 22)
  CAR_CONFIGURATOR_BUTTON =  ElementBB(9, 84, 99, 22)
  FIGURE_PRINTER_BUTTON = ElementBB(9, 112, 99, 22)

  #TODO: use MAIN_WINDOW_PAGES instead of PAGE_BB?
  PAGE_TEXT_PRINTER = PAGE_BB, "text_printer"
  PAGE_CALCULATOR = PAGE_BB, "calculator"
  PAGE_CAR_CONFIGURATOR = PAGE_BB, "car_configurator"
  PAGE_FIGURE_PRINTER = PAGE_BB, "figure_printer"

  SETTINGS_PAGE_TEXT_PRINTER = SETTINGS_PAGE_BB
  SETTINGS_PAGE_CALCULATOR = SETTINGS_PAGE_BB
  SETTINGS_PAGE_CAR_CONFIGURATOR = SETTINGS_PAGE_BB
  SETTINGS_PAGE_FIGURE_PRINTER = SETTINGS_PAGE_BB

  ## Settings

  SETTINGS_CLOSE_BUTTON = ElementBB(25, 318, 377, 27)

  SETTINGS_TEXT_PRINTER_TAB_BUTTON = ElementBB(25, 25, 85, 23), "settings_text_printer"
  SETTINGS_CALCULATOR_TAB_BUTTON = ElementBB(111, 25, 79, 23), "settings_calculator"
  SETTINGS_CAR_CONFIGURATOR_TAB_BUTTON = ElementBB(191, 25, 85, 23), "settings_car_configurator"
  SETTINGS_FIGURE_PRINTER_TAB_BUTTON = ElementBB(277, 25, 97, 23), "settings_figure_printer"

  ### Settings-Widgets
  SETTINGS_TEXT_PRINTER_WIDGET_BOLD = ElementBB(38, 215, 14, 14)

  ##Calculator
  OPERAND_ONE_DROPDOWN = ElementBB(125, 316, 97, 22)
  OPERAND_TWO_DROPDOWN= ElementBB(228, 316, 97, 22)
  OPERATOR_DROPDOWN= ElementBB(331, 316, 97, 22)
  CALCULATE_BUTTON= ElementBB(125, 406, 303, 22)
  CALCULATOR_RESULT = ElementBB(126, 40, 302, 207)
