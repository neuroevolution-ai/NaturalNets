import numpy as np

from typing import List
from naturalnets.environments.app.check_box import CheckBox
from naturalnets.environments.app.elements import Elements
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.widget import Widget


class TextPrinterSettings(Page):
    _STATE_LEN:int = 0
    _ACCESSOR:Elements = Elements.SETTINGS_TEXT_PRINTER_TAB_BUTTON
    _WIDGET_DICTS = [
      {
        "id": Elements.SETTINGS_TEXT_PRINTER_WIDGET_BOLD,
        "state_len": 1,
        "type": CheckBox,
        "args": {
          "bounding_box": Elements.SETTINGS_TEXT_PRINTER_WIDGET_BOLD.bounding_box
        },
      },
      {
        "id": Elements.SETTINGS_TEXT_PRINTER_WIDGET_ITALIC,
        "state_len": 1,
        "type": CheckBox,
        "args": {
          "bounding_box": Elements.SETTINGS_TEXT_PRINTER_WIDGET_ITALIC.bounding_box
        },
      },
      {
        "id": Elements.SETTINGS_TEXT_PRINTER_WIDGET_UNDERLINE,
        "state_len": 1,
        "type": CheckBox,
        "args": {
          "bounding_box": Elements.SETTINGS_TEXT_PRINTER_WIDGET_UNDERLINE.bounding_box
        },
      },
    ]

    @staticmethod
    def get_state_len(self):
        return self._STATE_LEN

    @staticmethod
    def get_widget_dicts(self):
        return self._WIDGETS_DICTS

    @staticmethod
    def get_accessor(self):
        return self._ACCESSOR

    def __init__(self, state_sector:np.ndarray, instantiatied_widgets:List[Widget]):
        self.widgets = instantiatied_widgets

    def handle_click(self):
        for widget in self.widgets:
            widget.handle_click()


    def render(self, img:np.ndarray):
        #TODO
        #for widget in self.widgets:
        #    widget.render(img)
        raise NotImplementedError("Implement render function of text-printer-settings!")



