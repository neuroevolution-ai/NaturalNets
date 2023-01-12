import os
import random

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from name_exists_popup_page import NameExistsPopupPage
from five_profiles_popup_page import FiveProfilesPopupPage
from naturalnets.environments.anki.profile import Profile, ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class AddProfilePopupPage(Page,RewardElement):

    """
    State description:
        state[0]: if this popup is open
        state[1]: if the text field is filled
    """
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "add_profile_popup.png")
    
    WINDOW_BB = BoundingBox(0, 0, 500, 111)
    OK_BB = BoundingBox(292, 70, 91, 26)
    TEXT_BB = BoundingBox(400, 38, 86, 22)
    CANCEL_BB = BoundingBox(393, 70, 92, 27)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AddProfilePopupPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.name_exists_popup = NameExistsPopupPage()
        self.five_profiles_popup = FiveProfilesPopupPage()

        self.add_child(self.name_exists_popup)
        self.add_child(self.five_profiles_popup)

        self.secure_random = random.SystemRandom()
        self.current_field_string = None
        
        self.text_button: Button = Button(self.TEXT_BB, self.set_current_field_string())
        self.ok_button: Button = Button(self.OK_BB, self.add_profile())
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close())
        self.close_window_button: Button = Button(self.CLOSE_WINDOW_BB, self.close())

        self.add_widgets([self.text_button,self.ok_button,self.cancel_button,self.close_window_button])

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
        elif(self.close_window_button.is_clicked_by(click_position)):
            self.close_window_button.handle_click(click_position)

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
        self.current_field_string = None
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])
    
    def set_current_field_string(self):
        self.register_selected_reward(["profile_name_clipboard","clicked"])
        self.current_field_string = self.secure_random.choice(ProfileDatabase().profile_names)
    
    def add_profile(self,name: str):
        if (self.current_field_string is None):
            return
        elif (not(ProfileDatabase().is_adding_allowed())):
            self.five_profiles_popup.open()
        elif (ProfileDatabase().is_included(name)):
            self.name_exists_popup.open()
        else:    
            ProfileDatabase().create_profile(self.current_field_string)
            self.current_field_string = None
            self.close()