import os

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class CheckMediaPage(Page,RewardElement):
    
    """
    STATE_LEN is whether this window is open or not
    """
    
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "check_media.png")
    
    WINDOW_BB = BoundingBox(0, 0, 622, 536)
    CLOSE_BB = BoundingBox(518, 497, 91, 26)
    WINDOW_CLOSE_BB = BoundingBox(476, 0, 42, 37)   
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CheckMediaPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.close_button: Button = Button(self.WINDOW_BB,self.close())
        self.window_close_button: Button = Button(self.CLOSE_BB,self.close())

        self.add_widgets([self.close_button, self.window_close_button])
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }

    def handle_click(self,click_position: np.ndarray):
        if self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
        elif self.window_close_button.is_clicked_by(click_position):
            self.window_close_button.is_clicked_by(click_position)
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]
