import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.app_components.page import Page
from naturalnets.environments.app_components.reward_element import RewardElement
from naturalnets.environments.app_components.utils import render_onto_bb
from naturalnets.environments.app_components.widgets.button import Button


class CheckMediaPage(Page, RewardElement):
    """
    Actually a filler page. Has nothing to do with the logic of the application.
    Serves providing reward to the agent.
    State description:
            state[0]: if this window is open
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "check_media_page.png")

    WINDOW_BB = BoundingBox(100, 100, 622, 499)
    CLOSE_BB = BoundingBox(619, 562, 81, 24)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.close_button = Button(self.CLOSE_BB, self.close)

    """
        Provides reward for opening and closing the page
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }
    """
        Checks if the close button is clicked and if yes then closes the page.
    """

    def handle_click(self, click_position: np.ndarray):
        if self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0

    def is_open(self) -> int:
        return self.get_state()[0]

    """
        Renders the image of the page
    """

    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img
