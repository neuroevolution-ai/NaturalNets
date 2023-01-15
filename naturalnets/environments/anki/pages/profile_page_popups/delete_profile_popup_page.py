import os
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from profile_page import ProfilePage
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class DeleteProfilePopupPage(Page,RewardElement):
    """
    State description:
        state[0]: if this window is open  
    """
    STATE_LEN = 1
    WINDOW_BB = BoundingBox(35, 210, 530, 113)
    IMG_PATH = os.path.join(IMAGES_PATH, "delete_profile_popup.png")
    YES_BUTTON_BB = BoundingBox(370, 285, 87, 24)
    NO_BUTTON_BB = BoundingBox(465, 285, 87, 24)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeleteProfilePopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.yes_button: Button = Button(self.YES_BUTTON_BB, self.delete_profile())
        self.no_button: Button = Button(self.NO_BUTTON_BB, self.close())

        self.add_widgets([self.yes_button, self.no_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "delete_profile": 0
        }


    def handle_click(self, click_position: np.ndarray) -> None:
        if self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
        elif self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def delete_profile(self):
        if(ProfileDatabase().is_removing_allowed()):
            ProfileDatabase().delete_profile(ProfileDatabase().profiles[ProfilePage().current_index])
            self.register_selected_reward(["delete_profile"])
            self.close()
    
    def render(self,img:np.ndarray):
        img = super().render(img)
        return img
        