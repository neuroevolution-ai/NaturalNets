import os
import numpy as np
from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH

from naturalnets.environments.app_components.page import Page
from naturalnets.environments.password_manager_app.page_manager import PageManager
from naturalnets.environments.app_components.widgets.button import Button
from naturalnets.environments.app_components.widgets.dropdown import Dropdown, DropdownItem


class Options(Page):
    """An option page that has no influance on the application."""

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "function_bar/options.png")

    BOUNDING_BOX = BoundingBox(0, 0, 448, 324)

    OK_BUTTON_BB = BoundingBox(166, 291, 45, 22)
    ABORT_BUTTON_BB = BoundingBox(218, 291, 63, 22)

    NAME_DD_BB = BoundingBox(12, 42, 360, 20)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)

        self.buttons = [
            Button(self.OK_BUTTON_BB, self.return_to_main_window),
            Button(self.ABORT_BUTTON_BB, self.return_to_main_window),
        ]

        self.name_one = DropdownItem("test", "test")
        self.name_two = DropdownItem("qwer", "qwer")
        self.name_three = DropdownItem("asdf", "asdf")
        self.dropdown = Dropdown(self.NAME_DD_BB, [self.name_one, self.name_two, self.name_three])

        self.add_widget(self.dropdown)
        self.opened_dd = None

    def return_to_main_window(self) -> None:
        PageManager.return_to_main_page()

        self.dropdown.set_selected_item(None)
        self.dropdown.close()
        self.opened_dd = None

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)
            self.opened_dd = None
            return

        for button in self.buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)

        if self.dropdown.is_clicked_by(click_position):
            self.dropdown.handle_click(click_position)

            if self.dropdown.is_open():
                self.opened_dd = self.dropdown
            return

    def render(self, img: np.ndarray) -> np.ndarray:
        """Renders this page onto the given image."""
        return super().render(img)
