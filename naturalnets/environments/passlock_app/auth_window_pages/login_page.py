from ast import List

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup


class LoginPage(Page, RewardElement):

    STATE_LEN = 0

    ENTER_PW_TEXTFIELD_BB = BoundingBox(9, 112, 99, 22)
    SHOW_PW_BUTTON_BB = BoundingBox(9, 112, 99, 22)
    LOGIN_BUTTON_BB = BoundingBox(9, 112, 99, 22)

    def __init__(self):

        Page.__init__(self)
        RewardElement.__init__(self)

        self.enter_pw_textfield = RadioButton(self.ENTER_PW_TEXTFIELD_BB, self.enter_pw_text())
        self.show_pw_button = Button(self.SHOW_PW_BUTTON_BB)
        self.login_button = Button(self.LOGIN_BUTTON_BB)

        self.radio_button_group = RadioButtonGroup(self.enter_pw_textfield)

        self.widgets: List[Widget] = [self.radio_button_group, self.show_pw_button, self.login_button]

        self.add_widgets(self.widgets)#

    def enter_pw_text(self):
        pass

    def render(self):
        pass

    def reset(self):
        pass 

    def handle_click(self, click_position: np.ndarray):
        pass  