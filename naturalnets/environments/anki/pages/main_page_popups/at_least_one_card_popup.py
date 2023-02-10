import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button


class AtLeastOneCardPopup(Page, RewardElement):
    """
    This popup appears when the user tries to remove
    the only card from the deck during a study session
    State description:
        state[0]: if this popup is open
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "at_least_one_card_popup.png")
    WINDOW_BB = BoundingBox(250, 250, 318, 121)

    OK_BUTTON_BB = BoundingBox(476, 339, 81, 23)

    """
    Singleton design pattern to ensure that at most one
    AtLeastOneCardPopup is present
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AtLeastOneCardPopup, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.ok_button: Button = Button(self.OK_BUTTON_BB, self.close)

    """
    Reward the agent for opening and closing the popup
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }
    """
    Checks if the ok button is clicked and if so closes the popup
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
