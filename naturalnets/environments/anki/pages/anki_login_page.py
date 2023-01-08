import os
import random
from naturalnets.environments.anki.anki_account import AnkiAccountDatabase
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class AnkiLoginPage(Page,RewardElement):
    
    """
    STATE_LEN is composed of if this page is open, if the username field is filled and
    if the password field is filled 
    """
    
    STATE_LEN = 3
    IMG_PATH = os.path.join(IMAGES_PATH, "add_profile_popup.png")

    WINDOW_BB = BoundingBox(0, 0, 278, 281)
    USERNAME_BB = BoundingBox(25, 121, 91, 26)
    PASSWORD_BB = BoundingBox(149, 121, 91, 26)
    OK_BB = BoundingBox(70, 243, 91, 26)
    CANCEL_BB = BoundingBox(170, 243, 91, 26)
    CLOSE_BB = BoundingBox(236, 0, 42, 37)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AnkiLoginPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self,self.STATE_LEN,self.WINDOW_BB,self.IMG_PATH)
        RewardElement.__init__(self)
        self.secure_random = random.SystemRandom()

        self.username_clipboard = None
        self.password_clipboard = None

        self.username_button: Button = Button(self.USERNAME_BB, self.set_password_clipboard())
        self.password_button: Button = Button(self.PASSWORD_BB, self.set_username_clipboard())
        self.ok_button: Button = Button(self.OK_BB, AnkiAccountDatabase().login())
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close())
        self.close_button: Button = Button(self.CLOSE_BB, self.close())

    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "username_clipboard": "clicked",
            "password_clipboard": "clicked"
        }
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]
    
    def set_username_clipboard(self):
        self.get_state()[1] = 1
        self.username_clipboard = self.secure_random.choice(AnkiAccountDatabase().anki_username_list)
    
    def set_password_clipboard(self):
        self.get_state()[2] = 1
        self.password_clipboard = self.secure_random.choice(AnkiAccountDatabase().anki_password_list)