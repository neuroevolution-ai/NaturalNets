import os
import random
import string
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class RenameProfilePage(RewardElement,Page):
    
    """
    STATE_LEN is composed of the states if this window is open and if the text field is filled
    """
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "rename_profile_popup.png")
    
    WINDOW_BB = BoundingBox(30, 200, 498, 111)
    OK_BB = BoundingBox(323, 270, 91, 26)
    TEXT_BB = BoundingBox(430, 238, 86, 22)
    CANCEL_BB = BoundingBox(424, 270, 92, 27)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(RenameProfilePage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.secure_random = random.SystemRandom()
        self.current_field_string = None
        
        self.text_button: Button = Button(self.TEXT_BB,self.set_current_field_string())
        self.ok_button: Button = Button(self.OK_BB, self.rename_profile())
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close())
    
    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "profile_name_clipboard": "clicked"
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.text_button.is_clicked_by(click_position)):
            self.text_button.handle_click(click_position)
        elif(self.ok_button.is_clicked_by(click_position)):
            self.ok_button.handle_click(click_position)
        elif(self.cancel_button.is_clicked_by(click_position)):
            self.cancel_button.handle_click(click_position)

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])
    
    def set_current_field_string(self):
        self.current_field_string = self.secure_random.choices(string.ascii_lowercase + string.digits, 10)
        self.register_selected_reward(["profile_name_clipboard","clicked"])
    
    def is_open(self) -> int:
        return self.get_state()[0]

    def rename_profile(self):
        if(self.current_field_string is not None):
            ProfileDatabase().rename_profile(self.current_field_string)