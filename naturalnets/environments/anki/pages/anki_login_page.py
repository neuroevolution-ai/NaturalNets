import os
import cv2
import numpy as np
from naturalnets.environments.anki import AnkiAccount
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.pages.main_page_popups.failed_login_popup import FailedLoginPopup
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button


class AnkiLoginPage(Page, RewardElement):
    """
    State description:
            state[0]: if this window is open
            state[i]: if the i-th field is filled i = [1:10] "one to ten including both"
            state[11]: if it's logged in
    """

    STATE_LEN = 12
    IMG_PATH = os.path.join(IMAGES_PATH, "anki_login_page.png")

    WINDOW_BB = BoundingBox(270, 250, 277, 244)
    USERNAME_BB = BoundingBox(279, 299, 121, 23)
    PASSWORD_BB = BoundingBox(419, 299, 121, 23)
    OK_BB = BoundingBox(312, 459, 82, 23)
    CANCEL_BB = BoundingBox(413, 459, 100, 23)

    USERNAME_X = 376
    USERNAME_Y = 363
    PASSWORD_X = 376
    PASSWORD_Y = 409

    def __init__(self):

        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.failed_login = FailedLoginPopup()
        # Anki Account is composed of a username and a password
        self.current_anki_account = None
        self.username_iterate_index = 0
        self.password_iterate_index = 0

        self.anki_username_list = ["account_1", "account_2", "account_3", "account_4", "account_5"]
        self.anki_password_list = ["pTgHAa", "L7WwEH", "yfTVwA", "DP7xg7", "zx7FeR"]

        self.username_clipboard = None
        self.password_clipboard = None

        self.username_button: Button = Button(self.USERNAME_BB, self.set_username_clipboard)
        self.password_button: Button = Button(self.PASSWORD_BB, self.set_password_clipboard)
        self.ok_button: Button = Button(self.OK_BB, self.login)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)

        self.add_child(self.failed_login)
        self.set_reward_children([self.failed_login])

    """
    Provides reward for opening and closing the page as well as setting username, password and logging in
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "set_username": 0,
            "set_password": 0,
            "login": 0
        }

    """
    Checks if both username and password strings are set
    """
    def is_strings_not_none(self):
        return self.username_clipboard is not None and self.password_clipboard is not None

    def get_current_account(self):
        return self.current_anki_account

    def open(self):
        self.get_state()[0] = 1
        self.get_state()[1:12] = 0
        self.username_clipboard = None
        self.password_clipboard = None
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0:12] = 0
        for child in self.get_children():
            child.close()
        self.username_clipboard = None
        self.password_clipboard = None

    def is_open(self):
        return self.get_state()[0]

    """
    Sets the password string from the username list 
    """
    def set_username_clipboard(self):
        self.username_clipboard = self.anki_username_list[self.username_iterate_index]
        self.get_state()[1 + (self.username_iterate_index - 1) % 5] = 0
        self.username_iterate_index += 1
        self.username_iterate_index %= 5
        self.get_state()[1 + (self.username_iterate_index - 1) % 5] = 1
        self.register_selected_reward(["set_username"])

    """
    Sets the password string from the password list 
    """
    def set_password_clipboard(self):
        self.password_clipboard = self.anki_password_list[self.password_iterate_index]
        self.get_state()[6 + (self.password_iterate_index - 1) % 5] = 0
        self.password_iterate_index += 1
        self.password_iterate_index %= 5
        self.get_state()[6 + (self.password_iterate_index - 1) % 5] = 1
        self.register_selected_reward(["set_password"])

    """
    Changes the current account if the login is allowed. Else opens error popup
    """
    def login(self):
        if not self.is_strings_not_none():
            return
        if self.is_allowed_login():
            self.register_selected_reward(["login"])
            self.current_anki_account = AnkiAccount(self.username_clipboard, self.password_clipboard)
            self.username_clipboard = None
            self.password_clipboard = None
            self.get_state()[11] = 1
            self.get_state()[1:11] = 0
            self.close()
        else:
            self.failed_login.open()

    """
    Resets the current account and username password combination.
    """
    def reset(self):
        self.current_anki_account = None
        self.username_clipboard = None
        self.password_clipboard = None
        self.get_state()[1:12] = 0

    """
    Renders anki login page with the failed login popup if open
    """
    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if self.failed_login.is_open():
            img = self.failed_login.render(img)
            return img
        if self.username_clipboard is not None:
            put_text(img, f"{self.username_clipboard}", (self.USERNAME_X, self.USERNAME_Y), font_scale=0.5)
        if self.password_clipboard is not None:
            put_text(img, f"{self.password_clipboard}", (self.PASSWORD_X, self.PASSWORD_Y), font_scale=0.5)
        return img

    """
    Delegates the click to the failed login popup if it is open.
    Else if a button is clicked the click action of this button
    is executed.
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.failed_login.is_open():
            self.failed_login.handle_click(click_position)
            return
        if self.username_button.is_clicked_by(click_position):
            self.username_button.handle_click(click_position)
        elif self.password_button.is_clicked_by(click_position):
            self.password_button.handle_click(click_position)
        elif self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
        elif self.cancel_button.is_clicked_by(click_position):
            self.cancel_button.handle_click(click_position)

    """
    Checks if the indices of the current username and password are the same.
    If true then the login is allowed
    """
    def is_allowed_login(self):
        if self.is_strings_not_none():
            return self.anki_username_list.index(self.username_clipboard) == self.anki_password_list.index(
                self.password_clipboard)
