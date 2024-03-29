import os
import numpy as np
from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH

from naturalnets.environments.app_components.page import Page
from naturalnets.environments.password_manager_app.page_manager import PageManager
from naturalnets.environments.app_components.widgets.button import Button
from naturalnets.environments.app_components.widgets.dropdown import Dropdown, DropdownItem


class FileSystem(Page):
    """Simulates a file system."""

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "function_bar/file_system.png")

    BOUNDING_BOX = BoundingBox(0, 0, 448, 448)

    SAVE_BUTTON_BB = BoundingBox(343, 388, 93, 66)
    ABORT_BUTTON_BB = BoundingBox(343, 415, 93, 66)

    NAME_DD_BB = BoundingBox(174, 389, 138, 20)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)

        self.buttons = [
            Button(self.SAVE_BUTTON_BB, self.return_to_main_window),
            Button(self.ABORT_BUTTON_BB, self.return_to_main_window),
        ]

        self.name_one = DropdownItem("Test1", "Test1")
        self.name_two = DropdownItem("Test2", "Test2")
        self.name_three = DropdownItem("Test3", "Test3")
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
