import os
import numpy as np
from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH

from naturalnets.environments.app_components.page import Page
from naturalnets.environments.password_manager_app.page_manager import PageManager
from naturalnets.environments.app_components.widgets.button import Button


class AccountBar(Page):
    """The menu for accounts on the function bar."""

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "function_bar/account.PNG")

    BOUNDING_BOX = BoundingBox(58, 4, 175, 179)
    MENU_AREA_BB = BoundingBox(58, 23, 175, 115)

    ADD_ACCOUNT_BUTTON_BB = BoundingBox(60, 25, 170, 22)
    EDIT_ACCOUNT_BUTTON_BB = BoundingBox(60, 48, 170, 22)
    DELETE_ACCOUNT_BUTTON_BB = BoundingBox(60, 71, 170, 22)
    VIEW_ACCOUNT_BUTTON_BB = BoundingBox(60, 94, 170, 22)
    COPY_USERNAME_BUTTON_BB = BoundingBox(60, 117, 170, 20)
    COPY_PASSWORD_BUTTON_BB = BoundingBox(60, 138, 170, 21)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)

        self.buttons = [
            Button(self.ADD_ACCOUNT_BUTTON_BB, lambda: PageManager.add_account()),
            Button(self.EDIT_ACCOUNT_BUTTON_BB, lambda: PageManager.edit_account()),
            Button(self.DELETE_ACCOUNT_BUTTON_BB, lambda: PageManager.delete_account()),
            Button(self.VIEW_ACCOUNT_BUTTON_BB, lambda: PageManager.view_account()),
            Button(self.COPY_USERNAME_BUTTON_BB, lambda: PageManager.copy_username()),
            Button(self.COPY_PASSWORD_BUTTON_BB, lambda: PageManager.copy_password()),
        ]

    def handle_click(self, click_position: np.ndarray = None) -> None:
        if self.MENU_AREA_BB.is_point_inside(click_position):
            self.handle_menu_click(click_position)
            return
        else:
            PageManager.return_to_main_page()

    def handle_menu_click(self, click_position: np.ndarray = None) -> None:
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)

    def render(self, img: np.ndarray) -> np.ndarray:
        """Renders this page onto the given image."""
        return super().render(img)
