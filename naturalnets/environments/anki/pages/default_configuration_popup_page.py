import os

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button


class DefaultConfigurationPopupPage(Page,RewardElement):
    
    """
    STATE_LEN is if this window is open or not
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "default_configuration_popup.png")
    
    WINDOW_BB = BoundingBox(0, 0, 381, 144)
    OK_BUTTON = BoundingBox(276, 106, 91, 26)
    CLOSE_BB = BoundingBox(354, 0, 41, 27)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DefaultConfigurationPopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.ok_button: Button = Button(self.OK_BUTTON,self.close())
        self.close_button: Button = Button(self.CLOSE_BB,self.close())

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }
    
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
        elif self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
    
    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])
    
    def is_open(self):
        return self.get_state()[0]