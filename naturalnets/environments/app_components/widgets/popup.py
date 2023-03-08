'''This module contains the PopUp class.'''
import numpy as np

from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.app_components.page import Page
from naturalnets.environments.app_components.reward_element import RewardElement


class PopUp(Page, RewardElement):
    """A popup that can be opened and closed. It is a page, so it can be rendered on an image.

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1

    def __init__(self, page_bounding_box: BoundingBox, popup_bb: BoundingBox, img_path: str):
        Page.__init__(self, self.STATE_LEN, page_bounding_box, img_path)
        RewardElement.__init__(self)
        self.popup_bb = popup_bb

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }

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
        if self.is_open():
            if self.popup_bb.is_point_inside(click_position):
                self.close_popup()
