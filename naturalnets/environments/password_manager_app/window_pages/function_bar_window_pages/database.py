import os
import numpy as np
from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH

from naturalnets.environments.app_components.page import Page
from naturalnets.environments.password_manager_app.page_manager import PageManager
from naturalnets.environments.app_components.widgets.button import Button


class Database(Page):
    """The menu for database on the function bar."""

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "function_bar/database.png")

    BOUNDING_BOX = BoundingBox(1, 3, 237, 254)
    MENU_AREA_BB = BoundingBox(1, 23, 237, 234)

    NEW_DATABASE_BUTTON_BB = BoundingBox(3, 25, 232, 22)
    OPEN_DATABASE_BUTTON_BB = BoundingBox(3, 48, 232, 22)
    Change_MASTER_PASSWORD_BUTTON_BB = BoundingBox(3, 125, 232, 22)
    EXPORT_BUTTON_BB = BoundingBox(3, 178, 232, 22)
    IMPORT_BUTTON_BB = BoundingBox(3, 201, 232, 22)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)

        self.buttons = [
            Button(self.NEW_DATABASE_BUTTON_BB, PageManager.open_file_system),
            Button(self.OPEN_DATABASE_BUTTON_BB, PageManager.open_file_system),
            Button(self.Change_MASTER_PASSWORD_BUTTON_BB, PageManager.open_master_password),
            Button(self.EXPORT_BUTTON_BB, PageManager.open_file_system),
            Button(self.IMPORT_BUTTON_BB, PageManager.open_file_system),
        ]

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.MENU_AREA_BB.is_point_inside(click_position):
            self.handle_menu_click(click_position)
            return
        else:
            PageManager.return_to_main_page()

    def handle_menu_click(self, click_position: np.ndarray) -> None:
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)

    def render(self, img: np.ndarray) -> np.ndarray:
        """Renders this page onto the given image."""
        return super().render(img)
