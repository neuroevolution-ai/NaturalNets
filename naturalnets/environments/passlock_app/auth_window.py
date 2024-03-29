"""The Authentication Window of the app, containing the different Authentication-pages, one for"""
import os
from typing import Dict, List

import numpy as np

from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.app_components.interfaces import Clickable
from naturalnets.environments.app_components.page import Page
from naturalnets.environments.app_components.reward_element import RewardElement
from naturalnets.environments.app_components.state_element import StateElement
from naturalnets.environments.passlock_app.auth_window_pages.login_page import LoginPage
from naturalnets.environments.passlock_app.auth_window_pages.signup_page import SignupPage
from naturalnets.environments.passlock_app.constants import IMAGES_PATH


class AuthenticationWindow(StateElement, Clickable, RewardElement):
    """The Authentication Window of the app, containing the different Authentication-pages, one for
        for login and one for signup.

       State description:
            state[0]: represents the open/closed status of the Authentication window.
            state[i]: represents the selected/shown status of page i, i in {0,1,2}.
    """

    STATE_LEN = 3
    IMG_PATH = os.path.join(
        IMAGES_PATH, "signup_page_img", "signup_window.png")
    APP_BOUNDING_BOX = BoundingBox(0, 0, 1920, 987)

    def __init__(self):
        StateElement.__init__(self, self.STATE_LEN)
        RewardElement.__init__(self)

        self._bounding_box = self.APP_BOUNDING_BOX

        self.login = LoginPage()
        self.signup = SignupPage()

        self.pages: List[Page] = [self.login, self.signup]
        assert len(self.pages) == self.get_state_len() - 1

        self.current_page = None

        self.add_children([self.login, self.signup])
        self.set_reward_children([self.login, self.signup])

        self.pages_to_str: Dict[Page, str] = {
            self.login: "login",
            self.signup: "signup",
        }

    @property
    def reward_template(self):
        '''
        Returns the reward template for the Authentication window.
        '''
        return {
            "auth_window": ["open", "close"],
            "page_selected": ["login", "signup"]
        }

    def set_current_page(self, page: Page):
        """Sets the currently selected/shown page, setting the respective
        state element to 1 and the state elements representing the other pages
        to 0.

        Args:
            page (Page): the page to be selected.
        """
        if self.current_page != page:
            self.get_state()[:] = 0
            self.get_state()[self.pages.index(page)] = 1
            self.open()
            self.current_page = page

            # noinspection PyTypeChecker
            self.register_selected_reward(
                ["page_selected", self.pages_to_str[self.current_page]])

    def reset(self):
        '''
        Resets the Authentication window to its initial state.
        '''
        self.login.reset()
        self.signup.reset()
        self.get_state()[:] = 0
        self.open()
        self.current_page = self.signup

    def is_open(self) -> int:
        """Returns if the settings window is open."""
        return self.get_state()[0]

    def open(self):
        """Opens the auth window."""
        self.register_selected_reward(["auth_window", "open"])

        self.get_state()[0] = 1

    def close(self):
        """Closes the settings window."""
        self.register_selected_reward(["auth_window", "close"])

        self.get_state()[0] = 0

    def handle_click(self, click_position: np.ndarray) -> bool:
        '''
        Handles a click on the Authentication window.
        If the login page is open it will handle the click on the login page.
        If the signup page is open it will handle the click on the signup page.
        If on the signup page a login or signup is successful it will return True.

        args: click_position: the position of the click.
        returns: True if a login or signup was successful, False otherwise.
        '''

        if self.current_page.handle_click(click_position):
            return True
        return False

    def render(self, img: np.ndarray) -> np.ndarray:
        """
        Renders the main window and all its children onto the given image.
        """

        if self.current_page == self.signup:
            img = self.signup.render(img)
        elif self.current_page == self.login:
            img = self.login.render(img)

        return img

    def get_bb(self) -> BoundingBox:
        '''
        Returns the bounding box of the Authentication window.
        '''
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        '''
        Sets the bounding box of the Authentication window.
        '''
        self._bounding_box = bounding_box

    def log_out(self):
        '''
        Signs up the user.
        '''
        self.set_current_page(self.login)
