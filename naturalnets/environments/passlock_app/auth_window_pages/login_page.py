from typing import List
import os
import cv2

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button, ShowPasswordButton
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup
from naturalnets.environments.passlock_app.constants import IMAGES_PATH, WINDOW_AREA_BB
from naturalnets.environments.passlock_app.utils import combine_path_for_image, draw_rectangle_from_bb, draw_rectangles_around_clickables, textfield_check
from naturalnets.environments.passlock_app.widgets.textfield import Textfield


class LoginPage(Page, RewardElement):
    '''
    The login page of the authentication window.
    '''

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "login_page_img/login_page.png")
    ENTER_PW_TEXTFIELD_BB = BoundingBox(288, 292, 1269, 75)
    SHOW_PW_BUTTON_BB = BoundingBox(1557, 292, 75, 75)
    LOGIN_BUTTON_BB = BoundingBox(903, 465, 112, 112)

    def __init__(self):

        Page.__init__(self, self.STATE_LEN, WINDOW_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.enter_pw_textfield = Textfield(self.ENTER_PW_TEXTFIELD_BB)
        self.show_pw_button = ShowPasswordButton(self.SHOW_PW_BUTTON_BB)
        self.login_button = Button(self.LOGIN_BUTTON_BB, lambda: self.login())

        self.buttons: List[Button] = [self.login_button, self.show_pw_button]
        self.textfields: List[Textfield] = [self.enter_pw_textfield]
        self.clickables = self.buttons + self.textfields
        self.widgets: List[Widget] = [
            self.enter_pw_textfield, self.show_pw_button]

        self.add_widget(self.enter_pw_textfield)
        self.add_widget(self.show_pw_button)
        print("Login Page Created")

    @property
    def reward_template(self):
        '''
        The reward template for the signup page. TODO: finish template
        '''
        return {

        }

    def login(self):
        '''
        This function is called when the login button is clicked.
        '''
        print("login")

    def render(self, img):
        """
        Renders the page onto the given image. 
        The image changes depending on the state of the page.

        args: img - the image to render onto
        returns: the rendered image
        """
        state = (
            textfield_check([self.enter_pw_textfield]),
            self.show_pw_button.is_password_shown()
        )

        img_paths = {
            (True, False): os.path.join(IMAGES_PATH, "login_page_img/login_page_pw.png"),
            (True, True): os.path.join(IMAGES_PATH, "login_page_img/login_page_showpw.png")
        }

        to_render = cv2.imread(img_paths.get(state, self.IMG_PATH))
        draw_rectangles_around_clickables(
            [self.buttons, self.textfields], to_render)
        img = to_render
        return img

    def reset(self):
        '''
        This function is called to reset the login page.
        '''
        self.enter_pw_textfield.set_selected(False)
        self.show_pw_button.showing_password = False

    def handle_click(self, click_position: np.ndarray):
        '''
        This function is called when the user clicks on the login page. 
        If the user clicks on a button, the button's function is called.

        args: click_position: the position of the click
        returns: True if the click resullts in a login 
        '''
        for clickable in self.clickables:
            if clickable.is_clicked_by(click_position):

                if (clickable == self.login_button and self.enter_pw_textfield.is_selected()):
                    clickable.handle_click(click_position)
                    return True
                else:
                    clickable.handle_click(click_position)
                    break
