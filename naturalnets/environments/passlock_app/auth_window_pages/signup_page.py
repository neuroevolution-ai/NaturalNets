import logging
import os
from typing import List

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import ORANGE_COLOR
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.widgets.button import (
    Button, ShowPasswordButton)
from naturalnets.environments.passlock_app.constants import (IMAGES_PATH,
                                                             WINDOW_AREA_BB)
from naturalnets.environments.passlock_app.utils import (
    draw_rectangles_around_clickables, textfield_check)
from naturalnets.environments.passlock_app.widgets.textfield import Textfield


class SignupPage(Page, RewardElement):
    '''
    The signup page of the authentication window.

    State Description:
    The Sigup Page has no state itself, but it contains the following widgets which have state:
        0: Email textfield is selected
        1: Password textfield is selected
        2: Whether or not the password is shown
    '''

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "signup_page_img", "signup_window.png")
    EMAIL_TEXTFIELD_BB = BoundingBox(288, 293, 1344, 75)
    PASSWORD_TEXTFIELD_BB = BoundingBox(288, 443, 1269, 75)
    SHOW_PW_BUTTON_BB = BoundingBox(1557, 443, 75, 75)
    SIGNUP_BUTTON_BB = BoundingBox(288, 593, 657, 66)
    LOGIN_BUTTON_BB = BoundingBox(975, 593, 657, 66)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, WINDOW_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.enter_email_textfield = Textfield(self.EMAIL_TEXTFIELD_BB, None, ORANGE_COLOR)
        self.enter_pw_textfield = Textfield(self.PASSWORD_TEXTFIELD_BB, None, ORANGE_COLOR)
        self.show_pw_button = ShowPasswordButton(self.SHOW_PW_BUTTON_BB, lambda: self.show_pw_button.show_password_of_textfield(self.enter_pw_textfield), ORANGE_COLOR)
        self.signup_button = Button(
            self.SIGNUP_BUTTON_BB, lambda: self.signup())
        self.login_button = Button(self.LOGIN_BUTTON_BB, lambda: self.login())

        self.buttons: List[Button] = [self.signup_button,
                                      self.login_button, self.show_pw_button]
        self.textfields: List[Textfield] = [
            self.enter_email_textfield, self.enter_pw_textfield]
        self.clickables = self.buttons + self.textfields

        self.reward_widgets_to_str = {
            self.enter_email_textfield: "enter_email_textfield",
            self.enter_pw_textfield: "enter_pw_textfield",
            self.show_pw_button: "show_pw_button",

        }

        self.add_widget(self.enter_email_textfield)
        self.add_widget(self.enter_pw_textfield)
        self.add_widget(self.show_pw_button)
        logging.debug("SignupPage init")

    @property
    def reward_template(self):
        '''
        The reward template for the signup page. 
        '''
        return {
            "enter_email_textfield": [False, True],
            "enter_pw_textfield": [False, True],
            "show_pw_button": [False, True],
        }

    def login(self):
        '''
        This function is called when the login button is clicked.
        '''
        logging.debug("login")

    def signup(self):
        '''
        This function is called when the signup button is clicked.
        '''
        logging.debug("signup")

    def reset(self):
        '''
        This function is called to reset the signup page.
        '''
        self.enter_email_textfield.set_selected(False)
        self.enter_pw_textfield.set_selected(False)
        self.show_pw_button.showing_password = False

    def handle_click(self, click_position: np.ndarray):
        '''
        This function is called when the user clicks on the signup page. 
        If the user clicks on a button, the button's function is called.

        args: click_position: the position of the click
        returns: True if the click resullts in a login or signup
        '''

        for clickable in self.clickables:
            if clickable.is_clicked_by(click_position):

                # If the user clicks on the signup or login button, trigger a login/signup
                if (clickable == self.signup_button or clickable == self.login_button):
                    # but only if the password and email textfields are selected
                    if (self.enter_pw_textfield.is_selected() and self.enter_email_textfield.is_selected()):
                        clickable.handle_click(click_position)
                        return True
                else:
                    # If the clickable has a selected state, register the reward when it is selected
                    if (isinstance(clickable, StateElement)):
                        self.register_selected_reward(
                            [self.reward_widgets_to_str[clickable], clickable.is_selected()])
                    clickable.handle_click(click_position)
                    return False
