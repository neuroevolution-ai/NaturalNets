import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.widgets.check_box import CheckBox
from naturalnets.environments.app.widgets.radio_button_group import RadioButton, RadioButtonGroup

class FigurePrinterSettings(Page):
    STATE_LEN = 0
    IMG_PATH = IMAGES_PATH + "figure_printer_settings.png"

    SHOW_FIG_PRINTER_BB = BoundingBox(38, 91, 141, 14)

    #color_rbg
    GREEN_RB_BB = BoundingBox(38, 225, 55, 14)
    BLUE_RB_BB = BoundingBox(38, 251, 47, 14)
    BLACK_RB_BB = BoundingBox(217, 225, 53, 14)
    BROWN_RB_BB = BoundingBox(217, 251, 57, 14)


    def __init__(self):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        self._show_fig_printer_checkbox = CheckBox(self.SHOW_FIG_PRINTER_BB)

        self.add_widget(self._show_fig_printer_checkbox)
        self.add_widget(self._get_color_rbg())

        pass

    def _get_color_rbg(self):
        rbg = RadioButtonGroup([RadioButton(self.BLACK_RB_BB)])
        rbg.add_radio_buttons([
            RadioButton(self.GREEN_RB_BB),
            RadioButton(self.BLUE_RB_BB),
            RadioButton(self.BROWN_RB_BB),
        ])
        return rbg

    
    def is_figure_printer_activated(self):
        return self._show_fig_printer_checkbox.is_selected()

    def handle_click(self, click_position: np.ndarray = None):
        if not self.is_figure_printer_activated():
           if self._show_fig_printer_checkbox.is_clicked_by(click_position):
                self._show_fig_printer_checkbox.handle_click()
        # other widgets only available when figure printer is activated
        else:
            for widget in self.get_widgets():
                if widget.is_clicked_by(click_position):
                    widget.handle_click(click_position)