import os

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.widgets.button import Button

class AtLeastOneProfilePopupPage(Page, RewardElement):
    """
    STATE_LEN is whether the window is open or not
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "at_least_one_profile_popup.png")
    WINDOW_BB = BoundingBox(0, 0, 318, 145)
    
    EXIT_BUTTON_BB = BoundingBox(276, 0, 42, 31)
    OK_BUTTON_BB = BoundingBox(212, 105, 91, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AtLeastOneProfilePopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.exit_button: Button = Button(self.EXIT_BUTTON_BB,self.close())
        self.ok_button: Button = Button(self.OK_BUTTON_BB,self.close())

        self.add_widgets([self.exit_button,self.ok_button])
    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }
    
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.exit_button.is_clicked_by(click_position):
            self.exit_button.handle_click(click_position)
        elif self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]
