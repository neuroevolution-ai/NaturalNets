import os
import cv2
import numpy as np

from naturalnets.environments.password_manager_app.account_manager.account_manager import AccountManager
from naturalnets.environments.password_manager_app.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH, NAME_ONE, NAME_THREE, NAME_TWO
from naturalnets.environments.password_manager_app.page import Page
from naturalnets.environments.password_manager_app.reward_element import RewardElement
from naturalnets.environments.password_manager_app.utils import render_onto_bb
from naturalnets.environments.password_manager_app.widgets.button import Button


class ConfirmDeleteAccount(Page, RewardElement):

    STATE_LEN = 3
    IMG_PATH = os.path.join(IMAGES_PATH, "")

    NAME_ACOOUNT_TO_DELETE = ''

    BOUNDING_BOX = BoundingBox(53, 142, 348, 122)

    YES_BUTTON_BB = BoundingBox(146, 233, 73, 24)
    NO_BUTTON_BB = BoundingBox(227, 233, 73, 24)
    X_BUTTON_BB = BoundingBox(374, 142, 26, 32)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.buttons = [
            Button(self.YES_BUTTON_BB, lambda: self.yes()),
            Button(self.NO_BUTTON_BB, lambda: self.no()),
            Button(self.X_BUTTON_BB, lambda: self.no()),
        ]

    def yes(self):
        AccountManager.delete_account(self.NAME_ACOOUNT_TO_DELETE)
        self.return_to_main_window()

    def no(self):
        self.return_to_main_window()

    def handle_click(self, click_position: np.ndarray = None):
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)

    def render(self, img: np.ndarray):
        """ Renders this page onto the given image.
        """

        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.BOUNDING_BOX, to_render)
        return img

    def set_name(self, account_name: str):
        self.NAME_ACOOUNT_TO_DELETE = account_name

        if self.NAME_ACOOUNT_TO_DELETE == NAME_ONE:
            self.IMG_PATH = os.path.join(IMAGES_PATH, "confirm_delete_account/delete_account_Hanna.PNG")
        elif self.NAME_ACOOUNT_TO_DELETE == NAME_TWO:
            self.IMG_PATH  = os.path.join(IMAGES_PATH, "confirm_delete_account/delete_account_Klaus.png")
        elif self.NAME_ACOOUNT_TO_DELETE == NAME_THREE:
            self.IMG_PATH  = os.path.join(IMAGES_PATH, "confirm_delete_account/delete_account_Mariam.png")

    def return_to_main_window(self):
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.set_current_page(None)

    @property
    def reward_template(self):
        return {
            "tire_20_setting": [False, True],
            "tire_22_setting": [False, True]
        }