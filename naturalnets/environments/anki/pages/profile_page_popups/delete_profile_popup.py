import os
import cv2

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.app_components.page import Page
from naturalnets.environments.app_components.reward_element import RewardElement
from naturalnets.environments.app_components.utils import render_onto_bb
from naturalnets.environments.app_components.widgets.button import Button


class DeleteProfilePopup(Page, RewardElement):
    """
    Popup asking if the currently active deck should be deleted.
    State description:
        state[0]: if this window is open
    """
    STATE_LEN = 1
    WINDOW_BB = BoundingBox(160, 300, 530, 113)
    IMG_PATH = os.path.join(IMAGES_PATH, "delete_profile_popup.png")
    YES_BUTTON_BB = BoundingBox(478, 376, 84, 26)
    NO_BUTTON_BB = BoundingBox(586, 375, 84, 26)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.profile_database = ProfileDatabase()
        self.yes_button: Button = Button(
            self.YES_BUTTON_BB, self.delete_profile)
        self.no_button: Button = Button(self.NO_BUTTON_BB, self.close)

    """
    Provide reward for opening/closing the window and deleting a profile
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "delete_profile": 0
        }
    """
    Trigger click action if one of the buttons is clicked
    """

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
        elif self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)
    """
    Open this popup
    """

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    """
    Close this popup
    """

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    """
    Return true if this popup is open
    """

    def is_open(self) -> int:
        return self.get_state()[0]

    """
    If more than a profile is present delete the currently selected profile
    """

    def delete_profile(self):
        if self.profile_database.is_removing_allowed():
            self.profile_database.delete_profile()
            self.register_selected_reward(["delete_profile"])
            self.close()

    """
    Render the image of this popup
    """

    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img
