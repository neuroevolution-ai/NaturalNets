import os
import numpy as np
from naturalnets.environments.password_manager_app.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH

from naturalnets.environments.password_manager_app.page import Page
from naturalnets.environments.password_manager_app.reward_element import RewardElement


class ConfirmDeleteAccount(Page, RewardElement):

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "")

    NAME_ACOOUNT_TO_DELETE = ''

    BOUNDING_BOX = BoundingBox(53, 142, 341, 122)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

    def handle_click(self, click_position: np.ndarray = None):
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                # check if figure printer button is visible
                button.handle_click(click_position)

    def render(self, img: np.ndarray):
        """ Renders the main window and all its children onto the given image.
        """
        self.IMG_PATH = os.path.join(IMAGES_PATH, "confirm_delete_account/delete_account_" + self.NAME_ACOOUNT_TO_DELETE)

        img = super().render(img)

        return img

    def set_name(self, account_name: str):
        NAME_ACOOUNT_TO_DELETE = account_name

    @property
    def reward_template(self):
        return {
            "tire_20_setting": [False, True],
            "tire_22_setting": [False, True]
        }