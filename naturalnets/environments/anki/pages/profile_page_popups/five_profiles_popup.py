import os
import random
import cv2

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button

class FiveProfilesPopup(Page, RewardElement):
    """
    Pops up as warning that 5 profiles are already present
    State description:
        state[0]: if this window is open  
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "five_profiles_popup.png")
    WINDOW_BB = BoundingBox(230, 300, 318, 121)
    OK_BB = BoundingBox(462, 384, 78, 31)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.ok_button = Button(self.OK_BB, self.close)

    """
    Provide reward for opening/closing window
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }
    """
    Execute click action if the ok button is clicked
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
    """
    Opens this popup
    """
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    """
    Closes this popup
    """
    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    """
    Returns true if this popup is open
    """
    def is_open(self):
        return self.get_state()[0]

    """
    Renders the image of this popup
    """
    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img