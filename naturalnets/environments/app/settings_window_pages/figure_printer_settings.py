import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.widgets.check_box import CheckBox

class FigurePrinterSettings(Page):
    STATE_LEN = 2
    IMG_PATH = IMAGES_PATH + "figure_printer_settings.png"

    SHOW_FIG_PRINTER_BB = BoundingBox(38, 91, 14, 14)

    def __init__(self):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        self._show_fig_printer_checkbox = CheckBox(self.SHOW_FIG_PRINTER_BB)
        self.add_widget(self._show_fig_printer_checkbox)
        self.add_child(self._show_fig_printer_checkbox)

        pass
    
    def is_figure_printer_activated(self):
        return self._show_fig_printer_checkbox.is_checked()

    def handle_click(self, click_position: np.ndarray = None):
        for widget in self.get_widgets():
            if widget.is_clicked_by(click_position):
                widget.handle_click()
        #TODO
        pass