import os
import random
import cv2
import numpy as np
from naturalnets.environments.anki import AnkiAccount
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.pages.main_page_popups.failed_login_popup_page import FailedLoginPopupPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button

class AnkiLoginPage(Page,RewardElement):
    
    """
   State description:
            state[0]: if this window is open
            state[i]: if the i-th field is filled i = {1,2}
            state[3]: if it's logged in
    """
    
    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "anki_login.png")

    WINDOW_BB = BoundingBox(200, 200, 277, 244)
    USERNAME_BB = BoundingBox(192, 283, 79, 28)
    PASSWORD_BB = BoundingBox(295, 283, 79, 28)
    OK_BB = BoundingBox(230, 407, 76, 26)
    CANCEL_BB = BoundingBox(316, 407, 76, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AnkiLoginPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        
        Page.__init__(self,self.STATE_LEN,self.WINDOW_BB,self.IMG_PATH)
        RewardElement.__init__(self)
        self.secure_random = random.SystemRandom()
        self.failed_login = FailedLoginPopupPage()
        
        self.current_anki_account: AnkiAccount = None
        self.anki_username_list = ["account_1","account_2","account_3","account_4","account_5"]
        self.anki_password_list = ["pTgHAa","L7WwEH","yfTVwA","DP7xg7","zx7FeR"]

        self.username_clipboard: str = None
        self.password_clipboard: str = None

        self.username_button: Button = Button(self.USERNAME_BB, self.set_username_clipboard)
        self.password_button: Button = Button(self.PASSWORD_BB, self.set_password_clipboard)
        self.ok_button: Button = Button(self.OK_BB, self.login)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)

        self.add_widgets([self.username_button, self.password_button, self.cancel_button, self.ok_button])
        self.set_reward_children([self.failed_login])

    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "set_username": 0,
            "set_password": 0,
            "login": 0
        }
    
    def is_strings_not_none(self):
        return self.username_clipboard is not None and self.password_clipboard is not None

    def open(self):
        self.get_state()[0] = 1
        self.username_clipboard = None
        self.password_clipboard = None
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.username_clipboard = None
        self.password_clipboard = None
        self.register_selected_reward(["window", "close"])

    def is_open(self):
        return self.get_state()[0]
    
    def set_username_clipboard(self):
        self.get_state()[1] = 1
        self.username_clipboard = self.secure_random.choice(self.anki_username_list)
        self.register_selected_reward(["set_username"])

    def set_password_clipboard(self):
        self.get_state()[2] = 1
        self.password_clipboard = self.secure_random.choice(self.anki_password_list)
        self.register_selected_reward(["set_password"])

    def login(self):
        if(self.is_allowed_login()):     
            self.current_anki_account = AnkiAccount(self.username_clipboard,self.password_clipboard)
            self.username_clipboard = None
            self.password_clipboard = None
            self.get_state()[3] = 1
            self.get_state()[2] = 0
            self.get_state()[1] = 0
            self.close()
        else:
            self.failed_login.open()
        
    def reset(self):
        self.current_anki_account = None
        self.username_clipboard = None
        self.password_clipboard = None
        self.get_state()[3] = 0
        self.get_state()[2] = 0
        self.get_state()[1] = 0
    
    def render(self,img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if(self.failed_login.is_open()):
            img = self.failed_login.render(img)
            return img
        if(self.username_clipboard is not None):
            put_text(img,f"{self.username_clipboard}", (295, 358) ,font_scale = 0.5)
        if(self.password_clipboard is not None):
            put_text(img,f"{self.password_clipboard}", (295, 390) ,font_scale = 0.5)
        return img

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.failed_login.is_open()):
            self.failed_login.handle_click(click_position)
            return
        if (self.username_button.is_clicked_by(click_position)):
            self.username_button.handle_click(click_position)
        elif (self.password_button.is_clicked_by(click_position)):
            self.password_button.handle_click(click_position)
        elif (self.ok_button.is_clicked_by(click_position)):
            self.ok_button.handle_click(click_position)
        elif (self.cancel_button.is_clicked_by(click_position)):
            self.cancel_button.handle_click(click_position)
    
    def default_login(self):
        self.active_account = AnkiAccount(self.anki_username_list[0],self.anki_password_list[0])
        self.username_clipboard = None
        self.password_clipboard = None
        self.get_state()[3] = 1
        self.get_state()[2] = 0
        self.get_state()[1] = 0

    def is_allowed_login(self):
        if(self.is_strings_not_none()):
            return self.anki_username_list.index(self.username_clipboard) ==  self.anki_password_list.index(self.password_clipboard)