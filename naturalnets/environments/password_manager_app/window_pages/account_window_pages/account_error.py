import os
import cv2
import numpy as np


from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import (
    IMAGES_PATH,
    NAME_ONE,
    NAME_THREE,
    NAME_TWO
)
from naturalnets.environments.app_components.page import Page
from naturalnets.environments.password_manager_app.page_manager import (
    PageManager
)
from naturalnets.environments.app_components.utils import render_onto_bb
from naturalnets.environments.app_components.widgets.button import Button


class AccountError(Page):
    """An error page that gets opened when an account is added or edited
    so that the username is the same as an already existing one."""

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "")

    NAME_ACCOUNT = ""

    BOUNDING_BOX = BoundingBox(58, 148, 328, 122)

    OK_BUTTON_BB = BoundingBox(188, 232, 73, 21)
    X_BUTTON_BB = BoundingBox(360, 148, 32, 31)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)

        self.buttons = [
            Button(self.OK_BUTTON_BB, self.yes),
            Button(self.X_BUTTON_BB, self.no)
        ]

    def yes(self) -> None:
        PageManager.return_to_main_page()

    def no(self) -> None:
        PageManager.return_to_main_page()

    def handle_click(self, click_position: np.ndarray = None) -> None:
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)

    def render(self, img: np.ndarray) -> np.ndarray:
        """Renders the main window and all its children onto the given
        image."""
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.BOUNDING_BOX, to_render)
        return img

    def set_name(self, account_name: str) -> None:
        self.NAME_ACCOUNT = account_name

        if self.NAME_ACCOUNT == NAME_ONE:
            self.IMG_PATH = os.path.join(
                IMAGES_PATH, "account_window/error_Hanna.png"
            )
        elif self.NAME_ACCOUNT == NAME_TWO:
            self.IMG_PATH = os.path.join(
                IMAGES_PATH, "account_window/error_Klaus.png"
            )
        elif self.NAME_ACCOUNT == NAME_THREE:
            self.IMG_PATH = os.path.join(
                IMAGES_PATH, "account_window/error_Mariam.png"
            )
