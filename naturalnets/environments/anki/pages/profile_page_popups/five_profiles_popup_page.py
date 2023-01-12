import os

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class FiveProfilesPopupPage(Page,RewardElement):

    """
    State description:
        state[0]: if this window is open  
    """
    
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "five_profiles_popup.png")
    WINDOW_BB = BoundingBox(0, 0, 317, 121)
    OK_BB = BoundingBox(212, 80, 92, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FiveProfilesPopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.ok_button = Button(self.OK_BB,self.close())
        self.add_widgets([self.ok_button,self.close_button])
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.ok_button.is_clicked_by(click_position)):
            self.ok_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]