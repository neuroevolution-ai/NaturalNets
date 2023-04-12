import os
import cv2
import numpy as np

from naturalnets.environments.password_manager_app.account_manager.account_manager import (
    AccountManager
)
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


class ConfirmDeleteAccount(Page):
    """Confirmation page that pops up when deleting an account."""

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "")

    NAME_ACCOUNT_TO_DELETE = ""

    BOUNDING_BOX = BoundingBox(53, 142, 348, 122)

    YES_BUTTON_BB = BoundingBox(146, 233, 73, 24)
    NO_BUTTON_BB = BoundingBox(227, 233, 73, 24)
    X_BUTTON_BB = BoundingBox(374, 142, 26, 32)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)

        self.buttons = [
            Button(self.YES_BUTTON_BB, self.yes),
            Button(self.NO_BUTTON_BB, self.no),
            Button(self.X_BUTTON_BB, self.no),
        ]

    def yes(self) -> None:
        AccountManager.delete_account(self.NAME_ACCOUNT_TO_DELETE)
        PageManager.return_to_main_page()

    def no(self) -> None:
        PageManager.return_to_main_page()

    def handle_click(self, click_position: np.ndarray) -> None:
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)

    def render(self, img: np.ndarray) -> np.ndarray:
        """Renders this page onto the given image."""

        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.BOUNDING_BOX, to_render)
        return img

    def set_name(self, account_name: str) -> None:
        self.NAME_ACCOUNT_TO_DELETE = account_name

        if self.NAME_ACCOUNT_TO_DELETE == NAME_ONE:
            self.IMG_PATH = os.path.join(IMAGES_PATH, "confirm_delete_account/delete_account_Hanna.png")
        elif self.NAME_ACCOUNT_TO_DELETE == NAME_TWO:
            self.IMG_PATH = os.path.join(IMAGES_PATH, "confirm_delete_account/delete_account_Klaus.png")
        elif self.NAME_ACCOUNT_TO_DELETE == NAME_THREE:
            self.IMG_PATH = os.path.join(IMAGES_PATH, "confirm_delete_account/delete_account_Mariam.png")
