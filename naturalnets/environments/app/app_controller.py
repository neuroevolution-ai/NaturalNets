import numpy as np
from naturalnets.environments.app.bounding_box import BoundingBox

from naturalnets.environments.app.main_window import MainWindow
from naturalnets.environments.app.settings_window import SettingsWindow
from naturalnets.environments.app.settings_window_pages.figure_printer_settings import FigurePrinterSettings
from naturalnets.environments.app.state_element import StateElement
from naturalnets.environments.app.widgets.button import Button


class AppController():
    SETTINGS_BUTTON_BB = BoundingBox(8, 0, 49, 18)

    def __init__(self):
        self.main_window = MainWindow()
        self.settings_window = SettingsWindow(self.main_window)
        
        self.settings_button = Button(self.SETTINGS_BUTTON_BB, lambda: self.settings_window.open())

        self._total_state_len = 0
        self._total_state_len += self.get_element_state_len(self.main_window)
        self._total_state_len += self.get_element_state_len(self.settings_window)

        self._state = np.zeros(self._total_state_len, dtype=int)
        self._last_allocated_state_index = 0

        self.assign_state(self.main_window)
        self.assign_state(self.settings_window)

    def get_element_state_len(self, stateElement:StateElement) -> int:
        accumulated_len = 0
        for child in stateElement.get_children():
            accumulated_len += self.get_element_state_len(child)
        accumulated_len += stateElement.get_state_len()
        return accumulated_len

    def assign_state(self, stateElement:StateElement) -> None:
        state_len = stateElement.get_state_len()
        state_sector = self.get_next_state_sector(state_len)
        stateElement.assign_state_sector(state_sector)

        for child in stateElement.get_children():
            self.assign_state(child)

    def get_next_state_sector(self, state_len):
        sector_end = self._last_allocated_state_index + state_len
        sector = self._state[self._last_allocated_state_index:sector_end]
        self._last_allocated_state_index = sector_end
        return sector

    def get_app_state(self):
        return self._state
    
    def handle_click(self, click_position:np.ndarray):
        if self.settings_window.is_open():
            self.settings_window.handle_click(click_position)
        elif not self.main_window.is_dropdown_open() and self.settings_button.is_clicked_by(click_position):
            self.settings_window.open()
        else:
            self.main_window.handle_click(click_position)

    def render(self, img:np.ndarray) -> np.ndarray:
        img = self.main_window.render(img)
        if self.settings_window.is_open():
            img = self.settings_window.render(img)
        return img


