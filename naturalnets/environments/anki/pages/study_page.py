import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement

class StudyPage(RewardElement,Page):

    WINDOW_BB = BoundingBox(0, 0, 831, 710)
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StudyPage, cls).__new__(cls)
        return cls.instance
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]
