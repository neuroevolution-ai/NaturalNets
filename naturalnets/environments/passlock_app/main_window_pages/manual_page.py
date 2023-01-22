
import os
from typing import List

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import (
    Button, ShowPasswordButton)
from naturalnets.environments.passlock_app.constants import (IMAGES_PATH,
                                                             WINDOW_AREA_BB)
from naturalnets.environments.passlock_app.utils import (
    draw_rectangles_around_clickables, textfield_check)
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
            self.NAME_OF_PW_TEXTFIELD_BB)
        self.enter_secret_password_textfield = Textfield(
            self.PASSWORD_TEXTFIELD_BB)
        self.show_password_button = ShowPasswordButton(self.SHOW_PW_BB)
        self.create_pw_button = Button(
            self.CREATE_PW_BB, lambda: self.create_pw())

        self.buttons: List[Button] = [
            self.create_pw_button, self.show_password_button]
        self.textfields: List[Textfield] = [
            self.enter_nameof_password_textfield, self.enter_secret_password_textfield]
        self.clickables = self.buttons + self.textfields

        self.add_widget(self.enter_nameof_password_textfield)
        self.add_widget(self.enter_secret_password_textfield)
        self.add_widget(self.show_password_button)
        print("ManualPage init")

    @property
    def reward_template(self):
        '''
        Returns the reward template for this page.
        '''
        return {

        }

    def reset(self):
        '''
        Resets the page to its initial state.
        '''
        self.enter_nameof_password_textfield.set_selected(False)
        self.enter_secret_password_textfield.set_selected(False)
        self.show_password_button.showing_password = False

    def handle_click(self, click_position: np.ndarray):
        '''
        Handles a click on the page.

        args: click_position - the position of the click
        '''
        for clickable in self.clickables:
            if clickable.is_clicked_by(click_position):
                clickable.handle_click(click_position)
                break

    def render(self, img: np.ndarray):
        """
        Renders the page onto the given image. 
        The image changes depending on the state of the page.

        args: img - the image to render onto
        returns: the rendered image
        """
        state = (
            textfield_check([self.enter_nameof_password_textfield]),
            textfield_check([self.enter_secret_password_textfield]),
            self.show_password_button.showing_password
        )

        img_paths = {
            (True, False, False): os.path.join(IMAGES_PATH, "manual_page_img\manual_page_nopw.png"),
            (False, True, False): os.path.join(IMAGES_PATH, "manual_page_img\manual_page_pw.png"),
            (True, True, False): os.path.join(IMAGES_PATH, "manual_page_img\manual_page_nopw_pw.png"),
            (False, True, True): os.path.join(IMAGES_PATH, "manual_page_img\manual_page_pwshown.png"),
            (True, True, True): os.path.join(IMAGES_PATH, "manual_page_img\manual_page_nopw_pwshwon.png"),
        }

        to_render = cv2.imread(img_paths.get(state, self.IMG_PATH))
        draw_rectangles_around_clickables(
            [self.buttons, self.textfields], to_render)
        img = to_render
        return img

    def create_pw(self):
        '''
        Creates a password if the textfields are filled. Currently only resets the page.
        '''
        if (self.enter_nameof_password_textfield.is_selected() and self.enter_secret_password_textfield.is_selected()):
            self.reset()
