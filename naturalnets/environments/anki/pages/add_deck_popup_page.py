import os
import random
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.widgets.button import Button
class AddDeckPopupPage(Page,RewardElement):
    """
    STATE_LEN is if 
    """
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "add_deck_popup.png")
    
    WINDOW_BB = BoundingBox(0, 0, 500, 147)
    OK_BB = BoundingBox(293, 106, 91, 26)
    TEXT_BB = BoundingBox(400, 74, 86, 22)
    CANCEL_BB = BoundingBox(394, 106, 92, 27)
    CLOSE_WINDOW_BB = BoundingBox(459, 0, 41, 37)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AddDeckPopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.secure_random = random.SystemRandom()
        self.current_field_string = None
        
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close())
        self.close_window_button: Button = Button(self.CLOSE_WINDOW_BB, self.close())


    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "deck_name_clipboard": "clicked"
        }

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def set_deck_name_clipboard(self):
        self.register_selected_reward(["profile_name_clipboard","clicked"])
        ProfileDatabase().set_current_field_string()