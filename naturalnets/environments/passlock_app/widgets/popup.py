import os

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.passlock_app.constants import IMAGES_PATH
from naturalnets.environments.passlock_app.utils import draw_rectangle_from_bb


class PopUp(Page, RewardElement):
    """A popup that can be opened and closed. It is a page, so it can be rendered on an image.

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(0, 0, 0, 0)
    IMG_PATH = os.path.join(IMAGES_PATH, "")

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }

    def render(self, img: np.ndarray) -> np.ndarray:
        '''
        Renders the popup on the given image.

        Args: 
            img: The image to render the popup on.
        Returns:
            The image with the rendered popup.
        '''

        img = super().render(img)
        draw_rectangle_from_bb(img, self.BOUNDING_BOX, (0, 0, 255), 2)

        return img

    def reset(self):
        '''
        Resets the popup to its initial state.
        '''
        self.close_popup()

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]

    def open_popup(self):
        '''
        Opens the popup.
        '''
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close_popup(self):
        '''
        Closes the popup.
        '''
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def handle_click(self, click_position: np.ndarray):
        '''
        Handles a click on the popup. Currently, the only action is to close the popup.
        '''
        if (self.is_open()):
            if (self.BOUNDING_BOX.is_point_inside(click_position)):
                self.close_popup()
