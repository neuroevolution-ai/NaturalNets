import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.app_components.page import Page
from naturalnets.environments.app_components.reward_element import RewardElement
from naturalnets.environments.app_components.utils import render_onto_bb
from naturalnets.environments.app_components.widgets.button import Button


class NoCardPopup(Page, RewardElement):
    """
    This popup appears when the user tries to study
    a deck without any card
    State description:
        state[0]: if this popup is open
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "no_card_popup.png")
    WINDOW_BB = BoundingBox(200, 250, 316, 120)

    OK_BUTTON_BB = BoundingBox(419, 333, 83, 25)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.ok_button: Button = Button(self.OK_BUTTON_BB, self.close)

    """
    Provide reward for opening and closing the popup
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }

    """
    Checks if the ok button is clicked and if so the popup is
    going to be closed
    """

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0

    def is_open(self) -> int:
        return self.get_state()[0]

    """
    Renders the image of the popup
    """

    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img
