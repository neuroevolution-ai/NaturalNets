import os
import time
from typing import List
import cv2

import numpy as np
from traitlets import EventHandler
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup
from naturalnets.environments.passlock_app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.passlock_app.utils import draw_rectangle_from_bb

class SignupPage(Page, RewardElement):
    '''
    The signup page of the authentication window.
    '''

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "signup_page_img/signup_window.png")
    EMAIL_TEXTFIELD_BB = BoundingBox(288, 368, 1344, 75)
    PASSWORD_TEXTFIELD_BB = BoundingBox(288, 518, 1344-75, 75)
    SHOW_PW_BUTTON_BB = BoundingBox(288+1344-75, 518, 75, 75) 
    SIGNUP_BUTTON_BB = BoundingBox(288, 659, 657, 66)
    LOGIN_BUTTON_BB = BoundingBox(975, 659, 657, 66)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.enter_email_textfield = RadioButton(self.EMAIL_TEXTFIELD_BB, None, lambda: self.enter_email_text())
        self.enter_pw_textfield = RadioButton(self.PASSWORD_TEXTFIELD_BB, None, lambda: self.enter_password_text())
        self.show_pw_radiobutton = RadioButton(self.SHOW_PW_BUTTON_BB, None, lambda: self.show_pw())
        self.signup_button = Button(self.SIGNUP_BUTTON_BB, lambda: self.signup())
        self.login_button = Button(self.LOGIN_BUTTON_BB, lambda: self.login())

        self.buttons: List[Button] = [self.signup_button, self.login_button]

        self.radio_button_group = RadioButtonGroup([self.enter_email_textfield, self.enter_pw_textfield, self.show_pw_radiobutton])
        
        self.widgets: List[Widget] = [self.radio_button_group]
        self.add_widgets(self.widgets)
        print("SignupPage init")

    @property
    def reward_template(self):
        '''
        The reward template for the signup page. TODO: finish template
        '''
        return {

        }

    def enter_email_text(self):
        '''
        This function is called when the email textfield is clicked.
        '''
        if(self.enter_email_textfield.is_selected()):
            self.enter_email_textfield.set_selected(False)
        else:
            self.enter_email_textfield.set_selected(True)

    def enter_password_text(self):
        '''
        This function is called when the password textfield is clicked.
        '''
        if(self.enter_pw_textfield.is_selected()):
            self.enter_pw_textfield.set_selected(False)
        else:
            self.enter_pw_textfield.set_selected(True)

    def show_pw(self):
        '''
        This function is called when the show password button is clicked.
        '''
        if(self.show_pw_radiobutton.is_selected()):
            self.show_pw_radiobutton.set_selected(False)
        else:
            self.show_pw_radiobutton.set_selected(True)       
           
    def render(self, img):
        """
        Renders the page onto the given image. 
        The image changes depending on the state of the page.

        args: img - the image to render onto
        returns: the rendered image
        """
    
        to_render = cv2.imread(self.IMG_PATH)

        if(self.enter_email_textfield.is_selected()):
            path = os.path.join(IMAGES_PATH, "signup_page_img/signup_window_email.png")
            to_render = cv2.imread(path)
        
        if(self.enter_pw_textfield.is_selected()):
            path = os.path.join(IMAGES_PATH, "signup_page_img/signup_window_pw.png")
            to_render = cv2.imread(path)
        
        if(self.enter_pw_textfield.is_selected() and self.enter_email_textfield.is_selected()):
            path = os.path.join(IMAGES_PATH, "signup_page_img/signup_window_email_pw.png")
            to_render = cv2.imread(path)
        
        if(self.show_pw_radiobutton.is_selected()  
            and self.enter_pw_textfield.is_selected()):
            path = os.path.join(IMAGES_PATH, "signup_page_img/signup_window_pwshown.png")
            to_render = cv2.imread(path)

        if(self.show_pw_radiobutton.is_selected() 
            and self.enter_email_textfield.is_selected() 
            and self.enter_pw_textfield.is_selected()):
            path = os.path.join(IMAGES_PATH, "signup_page_img/signup_window_email_pwshown.png")
            to_render = cv2.imread(path)
   
        for button in self.buttons:
            draw_rectangle_from_bb(to_render, button._bounding_box, (0, 255, 0), 2)

        for rbg in self.radio_button_group.radio_buttons:
            draw_rectangle_from_bb(to_render, rbg._bounding_box, (0, 255, 0), 2)

        img = to_render
        return img

    def login(self):
        '''
        This function is called when the login button is clicked.
        '''
        print("login")     

    def signup(self):
        '''
        This function is called when the signup button is clicked.
        '''
        print("signup")

    def reset(self):
        '''
        This function is called to reset the signup page.
        '''    
        self.enter_email_textfield.set_selected(False)
        self.enter_pw_textfield.set_selected(False)
        self.show_pw_radiobutton.set_selected(False)
        
    def handle_click(self, click_position: np.ndarray):
        '''
        This function is called when the user clicks on the signup page. 
        If the user clicks on a button, the button's function is called.

        args: click_position: the position of the click
        returns: True if the click resullts in a login or signup
        '''
        
        for button in self.buttons:
            if button.is_clicked_by(click_position):

                if(button == self.signup_button or button == self.login_button):
                    if(self.enter_pw_textfield.is_selected() and self.enter_email_textfield.is_selected()):
                        button.handle_click(click_position)
                        return True
                else:
                    button.handle_click(click_position)
                    
                break
        
        self.radio_button_group.handle_click(click_position)
        
       
   
            
        
    