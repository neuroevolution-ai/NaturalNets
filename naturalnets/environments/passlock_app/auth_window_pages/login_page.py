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
from naturalnets.environments.passlock_app.widgets.textfield import Textfield


class LoginPage(Page, RewardElement):
    '''
    The login page of the authentication window.

    State Description:
    The Login Page has no state itself, but it contains the following widgets which have state:
        0: Password textfield is selected
        1: Whether or not the password is shown     
    '''

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "login_page_img", "login_page.png")
    ENTER_PW_TEXTFIELD_BB = BoundingBox(288, 292, 1269, 75)
    SHOW_PW_BUTTON_BB = BoundingBox(1557, 292, 75, 75)
    LOGIN_BUTTON_BB = BoundingBox(903, 465, 112, 112)

    def __init__(self):

        Page.__init__(self, self.STATE_LEN, WINDOW_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.enter_pw_textfield = Textfield(self.ENTER_PW_TEXTFIELD_BB, None, ORANGE_COLOR)
        self.show_pw_button = ShowPasswordButton(self.SHOW_PW_BUTTON_BB, lambda: self.show_pw_button.show_password_of_textfield(self.enter_pw_textfield), ORANGE_COLOR)
        self.login_button = Button(self.LOGIN_BUTTON_BB, self.login)

        self.buttons: List[Button] = [self.login_button, self.show_pw_button]
        self.textfields: List[Textfield] = [self.enter_pw_textfield]
        self.clickables = self.buttons + self.textfields
        self.widgets: List[Widget] = [
            self.enter_pw_textfield, self.show_pw_button]

        self.reward_widgets_to_str = {
            self.enter_pw_textfield: "enter_pw_textfield",
            self.show_pw_button: "show_pw_button",
        }

        self.add_widget(self.enter_pw_textfield)
        self.add_widget(self.show_pw_button)
        logging.debug("Login Page Created")

    @property
    def reward_template(self):
        '''
        The reward template for the signup page. 
        '''
        return {
            "enter_pw_textfield": [False, True],
            "show_pw_button": [False, True]
        }

    def login(self):
        '''
        This function is called when the login button is clicked.
        '''
        logging.debug("login")

    def reset(self):
        '''
        This function is called to reset the login page.
        '''
        self.enter_pw_textfield.set_selected(False)
        self.show_pw_button.showing_password = False

    def handle_click(self, click_position: np.ndarray) -> bool:
        '''
        This function is called when the user clicks on the login page. 
        If the user clicks on a button, the button's function is called.

        args: click_position: the position of the click
        returns: True if the click resullts in a login 
        '''
        for clickable in self.clickables:
            if clickable.is_clicked_by(click_position):

                # If the user clicks on the login button, check if the password textfield is selected
                # If it is, then login
                if (clickable == self.login_button and self.enter_pw_textfield.is_selected()):
                    clickable.handle_click(click_position)
                    return True
                else:
                    # If the clickable has a state, register the reward when it is selected
                    if (isinstance(clickable, StateElement)):
                        self.register_selected_reward(
                            [self.reward_widgets_to_str[clickable], clickable.is_selected()])
                    clickable.handle_click(click_position)
                    return False
