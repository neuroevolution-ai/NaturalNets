
import logging
import os
from typing import List

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import ORANGE_COLOR
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.widgets.button import (
    Button, ShowPasswordButton)
from naturalnets.environments.passlock_app.constants import (IMAGES_PATH,
                                                             WINDOW_AREA_BB)

from naturalnets.environments.passlock_app.widgets.textfield import Textfield


class ManualPage(Page, RewardElement):
    '''
    The page that is shown when the user clicks on the manual button.

    State Description:
    The Manual Page has no state itself, but it has a state for each of its widgets with a inherent state.
        0: The state of the enter_nameof_password_textfield
        1: The state of the enter_secret_password_textfield
        2: The state of the show_password_button
    '''
    ### Constants ###
    STATE_LEN = 0
    NAME_OF_PW_TEXTFIELD_BB = BoundingBox(280, 155, 1479, 75)
    PASSWORD_TEXTFIELD_BB = BoundingBox(280, 305, 1404, 75)
    CREATE_PW_BB = BoundingBox(280, 417, 1479, 74)
    SHOW_PW_BB = BoundingBox(1684, 305, 75, 75)
    IMG_PATH = os.path.join(IMAGES_PATH, "home_window.png")

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, WINDOW_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.enter_nameof_password_textfield = Textfield(
            self.NAME_OF_PW_TEXTFIELD_BB, None, ORANGE_COLOR)
        self.enter_secret_password_textfield = Textfield(
            self.PASSWORD_TEXTFIELD_BB, None, ORANGE_COLOR)
        self.show_password_button = ShowPasswordButton(self.SHOW_PW_BB, None, ORANGE_COLOR)
        self.create_pw_button = Button(
            self.CREATE_PW_BB, lambda: self.create_pw())

        self.buttons: List[Button] = [
            self.create_pw_button, self.show_password_button]
        self.textfields: List[Textfield] = [
            self.enter_nameof_password_textfield, self.enter_secret_password_textfield]
        self.clickables = self.buttons + self.textfields

        self.reward_widgets_to_str = {
            self.enter_nameof_password_textfield: "enter_nameof_password_textfield",
            self.enter_secret_password_textfield: "enter_secret_password_textfield",
            self.show_password_button: "show_password_button",
        }


        self.add_widget(self.enter_nameof_password_textfield)
        self.add_widget(self.enter_secret_password_textfield)
        self.add_widget(self.show_password_button)
        logging.debug("ManualPage init")

    @property
    def reward_template(self):
        '''
        Returns the reward template for this page.
        '''
        return {
            "enter_nameof_password_textfield": [False, True],
            "enter_secret_password_textfield": [False, True],
            "show_password_button": [False, True],

        }

    def reset(self):
        '''
        Resets the page to its initial state.
        '''
        self.enter_nameof_password_textfield.set_selected(False)
        self.enter_secret_password_textfield.set_selected(False)
        self.show_password_button.set_selected(False)

    def handle_click(self, click_position: np.ndarray):
        '''
        Handles a click on the page.

        args: click_position - the position of the click
        '''
        for clickable in self.clickables:
            if clickable.is_clicked_by(click_position):

                try:
                    rew_key = self.reward_widgets_to_str[clickable]
                    #If the clickable has a selected state, register the reward when it is selected
                    self.register_selected_reward([self.reward_widgets_to_str[clickable], clickable.is_selected()])
                except KeyError:
                    pass  # This clickable does not grant a reward, continue     
                   
                clickable.handle_click(click_position)
                break

    def create_pw(self):
        '''
        Creates a password if the textfields are filled. Currently only resets the page.
        '''
        if (self.enter_nameof_password_textfield.is_selected() and self.enter_secret_password_textfield.is_selected()):
            self.enter_nameof_password_textfield.reset()
            self.enter_secret_password_textfield.reset()
