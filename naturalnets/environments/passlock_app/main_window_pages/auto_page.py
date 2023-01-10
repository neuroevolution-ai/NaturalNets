from typing import List
import os

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup
from naturalnets.environments.passlock_app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.passlock_app.widgets.slider import Slider


class AutoPage(Page, RewardElement):

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "calculator.png")
    TEXTFIELD_1_BB = BoundingBox(125, 316, 97, 22)
    TEXTFIELD_2_BB = BoundingBox(125, 316, 97, 22)
    CREATE_PW_BB = BoundingBox(9, 112, 99, 22)
    RESET_PW_BB = BoundingBox(9, 112, 99, 22)
    COPY_PW_BB = BoundingBox(9, 112, 99, 22)
    PW_LENGTH_BB = BoundingBox(9, 112, 99, 22)
    USE_LETTERS_BB = BoundingBox(9, 112, 99, 22)
    USE_NUMBERS_BB = BoundingBox(9, 112, 99, 22)
    USE_SPECIAL_CHARS_BB = BoundingBox(9, 112, 99, 22)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.is_nameof_password_visible = 0
        self.enter_nameof_password_radiobutton = RadioButton(
            self.TEXTFIELD_1_BB,
            lambda: self.enter_nameof_password()
        )

        self.is_password_visible = 0
        self.enter_secret_password_radiobutton = RadioButton(
            self.TEXTFIELD_2_BB,
            lambda: self.enter_password()
        )

        self.radio_button_group = RadioButtonGroup([self.enter_secret_password_radiobutton, self.enter_nameof_password_radiobutton])

        self.copy_pw_button = Button(self.COPY_PW_BB, lambda: self.nothing())
        self.reset_pw_button = Button(self.RESET_PW_BB, lambda: self.nothing())
        self.create_pw_button = Button(self.CREATE_PW_BB, lambda: self.nothing())
        self.pw_length_slider = Slider(self.PW_LENGTH_BB, 3)
        self.use_letters_checkbox = CheckBox(self.USE_LETTERS_BB)
        self.use_numbers_checkbox = CheckBox(self.USE_NUMBERS_BB)
        self.use_special_chars_checkbox = CheckBox(self.USE_SPECIAL_CHARS_BB)

        self.widgets: List[Widget] = [self.use_letters_checkbox,
                                        self.use_numbers_checkbox, 
                                        self.use_special_chars_checkbox]
        
        self.add_widget(self.radio_button_group)
        #self.add_widget(self.copy_pw_button)
        #self.add_widget(self.reset_pw_button)
        #self.add_widget(self.create_pw_button)
        self.add_widget(self.pw_length_slider)
        self.add_widget(self.use_letters_checkbox)
        self.add_widget(self.use_numbers_checkbox)
        self.add_widget(self.use_special_chars_checkbox)
        print("AutoPage created")

    @property
    def reward_template(self):
        return {

        }

    def enter_nameof_password(self):
        pass

    def enter_password(self):
        pass

    def render(self):
        pass

    def reset(self):
        pass 

    def handle_click(self, click_position: np.ndarray):
        pass 

    def nothing(self):
        pass 