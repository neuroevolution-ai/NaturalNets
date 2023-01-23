import os

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.passlock_app.constants import IMAGES_PATH
from naturalnets.environments.passlock_app.utils import combine_path_for_image, draw_rectangle_from_bb


class PopUp(Page, RewardElement):
    """Popup for the calculator settings (pops up when no operator-checkbox is selected).

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(0, 0, 0, 0)
    IMG_PATH = os.path.join(IMAGES_PATH, "")

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
        self.IMG_PATH = self.IMG_PATH
        self.BOUNDING_BOX = self.BOUNDING_BOX


    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }

    def render(self, img):
        '''
        Renders the popup on the given image.
        '''
        to_render = cv2.imread(self.IMG_PATH)
        draw_rectangle_from_bb(to_render, self.BOUNDING_BOX, (0, 0, 255), 2)
        img = to_render

        return img

    def reset(self):
        self.close_popup()

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]

    def open_popup(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close_popup(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def handle_click(self, click_position: np.ndarray):
        '''
        Handles a click on the popup. Currently, the only action is to close the popup.
        '''
        if (self.is_open()):
            if (self.BOUNDING_BOX.is_point_inside(click_position)):
                self.close_popup()
                return
