import os
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class FiveDecksPopupPage(Page,RewardElement):

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "five_decks_popup.png")
    WINDOW_BB = BoundingBox(0, 0, 319, 146)
    OK_BB = BoundingBox(212, 105, 92, 26)
    CLOSE_WINDOW_BB = BoundingBox(278, 0, 41, 28)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FiveDecksPopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.ok_button = Button(self.OK_BB,self.close())
        self.close_button = Button(self.CLOSE_WINDOW_BB,self.close())
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
        }

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]