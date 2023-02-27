"""This module contains the AutoPage class which is the page where the user can generate a password. The actual generation of the passwords is only modelled. No actual password is generated and the UI is not changed on generation of a password."""
import logging
import os
from typing import List

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import ORANGE_COLOR
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.passlock_app.constants import (IMAGES_PATH,
                                                             WINDOW_AREA_BB)
from naturalnets.environments.passlock_app.widgets.slider import Slider
from naturalnets.environments.passlock_app.widgets.textfield import Textfield


class AutoPage(Page, RewardElement):
    '''
    The AutoPage is the page where the user can generate a password. The actual generation of the passwords is only modelled.
    No actual password is generated and the UI is not changed on generation of a password.

    State Description:
        The Auto Page has no state itself, but it contains the following widgets which have state:
        0: Auto textfield is selected
        1: Password textfield is selected
        2: The length of the password
        3: Whether or not to use letters
        4: Whether or not to use numbers
        5: Whether or not to use special characters
    '''

    ### Constants###
    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "auto_page_img", "auto_page.png")
    NAME_OF_PW_TEXTFIELD_BB = BoundingBox(280, 155, 1479, 75)
    PASSWORD_TEXTFIELD_BB = BoundingBox(280, 305, 1329, 75)
    GENERATE_PW_BB = BoundingBox(280, 513, 1479, 75)
    RESET_PW_BB = BoundingBox(1684, 305, 75, 75)
    COPY_PW_BB = BoundingBox(1609, 305, 75, 75)
    PW_LENGTH_BB = BoundingBox(320, 413, 1439, 75)
    USE_LETTERS_BB = BoundingBox(293, 640, 28, 28)
    USE_NUMBERS_BB = BoundingBox(293, 694, 28, 28)
    USE_SPECIAL_CHARS_BB = BoundingBox(293, 749, 28, 28)

    def __init__(self):
        '''
        Initializes the AutoPage.
        '''
        Page.__init__(self, self.STATE_LEN, WINDOW_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.enter_nameof_password_textfield = Textfield(
            self.NAME_OF_PW_TEXTFIELD_BB, None, ORANGE_COLOR)
        self.enter_password_textfield = Textfield(self.PASSWORD_TEXTFIELD_BB, None, ORANGE_COLOR)

        self.copy_pw_button = Button(
            self.COPY_PW_BB, lambda: self.copy_password)
        self.reset_pw_button = Button(
            self.RESET_PW_BB, self.enter_password_textfield.reset)
        self.create_pw_button = Button(
            self.GENERATE_PW_BB, self.generate_password)
        self.pw_length_slider = Slider(self.PW_LENGTH_BB, 10, color=ORANGE_COLOR)

        self.use_letters_checkbox = CheckBox(self.USE_LETTERS_BB, None, ORANGE_COLOR)
        self.use_numbers_checkbox = CheckBox(self.USE_NUMBERS_BB, None, ORANGE_COLOR)
        self.use_special_chars_checkbox = CheckBox(self.USE_SPECIAL_CHARS_BB, None, ORANGE_COLOR)

        self.sliders: List[Slider] = [self.pw_length_slider]
        self.checkboxes: List[CheckBox] = [self.use_letters_checkbox,
                                           self.use_numbers_checkbox, self.use_special_chars_checkbox]
        self.textfields: List[Textfield] = [
            self.enter_nameof_password_textfield, self.enter_password_textfield]
        self.buttons: List[Button] = [self.copy_pw_button,
                                      self.reset_pw_button, self.create_pw_button]
        self.widgets: List[Widget] = [self.use_letters_checkbox,
                                      self.use_numbers_checkbox, self.use_special_chars_checkbox]
        self.clickables = self.sliders + self.checkboxes + self.textfields + self.buttons

        self.reward_widgets_to_str = {
            self.enter_nameof_password_textfield: "enter_nameof_password_textfield",
            self.enter_password_textfield: "enter_password_textfield",
            self.pw_length_slider: "pw_length_slider",
            self.use_letters_checkbox: "use_letters_checkbox",
            self.use_numbers_checkbox: "use_numbers_checkbox",
            self.use_special_chars_checkbox: "use_special_chars_checkbox",
            self.copy_pw_button: "copy_pw_button",
            self.reset_pw_button: "reset_pw_button",
            self.create_pw_button: "create_pw_button",
        }

        self.add_widget(self.pw_length_slider)
        self.add_widget(self.use_letters_checkbox)
        self.add_widget(self.use_numbers_checkbox)
        self.add_widget(self.use_special_chars_checkbox)
        self.add_widget(self.enter_nameof_password_textfield)
        self.add_widget(self.enter_password_textfield)

        logging.debug("AutoPage created")

    @property
    def reward_template(self):
        '''
        Returns the reward template for this page.
        '''
        return {
            "enter_nameof_password_textfield": [False, True],
            "enter_password_textfield": [False, True],
            # is manually set to 10 for the different states of the slider because this is setup before the slider is created
            "pw_length_slider": [i for i in range(10)],
            "use_letters_checkbox": [False, True],
            "use_numbers_checkbox": [False, True],
            "use_special_chars_checkbox": [False, True],
            "copy_pw_button": ["clicked"],
            "reset_pw_button": ["clicked"],
            "create_pw_button": ["clicked"],
        }

    def reset(self):
        '''
        Resets the page to its initial state.
        '''
        self.enter_nameof_password_textfield.reset()
        self.enter_password_textfield.reset()
        self.use_letters_checkbox.reset()
        self.use_numbers_checkbox.reset()
        self.use_special_chars_checkbox.reset()
        self.pw_length_slider.reset()

    def handle_click(self, click_position: np.ndarray) -> bool:
        '''
        Handles a click on the page.

        args: click_position - the position of the click
        returns: False, because only a login, signup or logout should return True
        '''

        for clickable in self.clickables:
            if clickable.is_clicked_by(click_position):

                try:
                    rew_key = self.reward_widgets_to_str[clickable]

                    if rew_key == "pw_length_slider":
                        self.register_selected_reward(
                            [self.reward_widgets_to_str[clickable], clickable.get_slider_value()])
                    elif isinstance(clickable, Button):
                        self.register_selected_reward(
                            [self.reward_widgets_to_str[clickable], "clicked"])
                    else:
                        self.register_selected_reward(
                            [self.reward_widgets_to_str[clickable], clickable.is_selected()])
                except KeyError:
                    pass  # This clickable does not grant a reward, continue
                clickable.handle_click(click_position)
                return False

    def copy_password(self):
        '''
        Method to copy the password to the clipboard.
        '''
        logging.debug("copied password")

    def generate_password(self):
        '''
        Method to generate a password. Currently just resets the page.
        '''
        if self.enter_password_textfield.is_selected() and self.enter_nameof_password_textfield.is_selected():
            self.enter_password_textfield.reset()
            self.enter_nameof_password_textfield.reset()
