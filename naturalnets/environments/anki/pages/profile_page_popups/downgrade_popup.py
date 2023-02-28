import os
import cv2

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button


class DowngradePopup(Page, RewardElement):
    """
    Filler popup. Does nothing.
    State description:
        state[0]: if this window is open

    """
    STATE_LEN = 1
    WINDOW_BB = BoundingBox(160, 300, 530, 113)
    IMG_PATH = os.path.join(IMAGES_PATH, "downgrade_popup.png")
    OK_BUTTON_BB = BoundingBox(601, 382, 81, 25)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.ok_button = Button(self.OK_BUTTON_BB, self.close)

    """
    Provide reward for opening/closing this popup
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }

    """
    Execute click action if a button is clicked"
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
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
    Render the image of this popup
    """
    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img
