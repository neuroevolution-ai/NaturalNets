import os
from typing import List
import cv2
import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button, ShowPasswordButton
from naturalnets.environments.passlock_app.constants import IMAGES_PATH, WINDOW_AREA_BB
from naturalnets.environments.passlock_app.utils import combine_path_for_image, draw_rectangles_around_clickables, textfield_check
from naturalnets.environments.passlock_app.widgets.textfield import Textfield


class SignupPage(Page, RewardElement):
    '''
    The signup page of the authentication window.
    '''

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "signup_page_img/signup_window.png")
    EMAIL_TEXTFIELD_BB = BoundingBox(288, 293, 1344, 75)
    PASSWORD_TEXTFIELD_BB = BoundingBox(288, 443, 1269, 75)
    SHOW_PW_BUTTON_BB = BoundingBox(1557, 443, 75, 75) 
    SIGNUP_BUTTON_BB = BoundingBox(288, 593, 657, 66)
    LOGIN_BUTTON_BB = BoundingBox(975, 593, 657, 66)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, WINDOW_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.enter_email_textfield = Textfield(self.EMAIL_TEXTFIELD_BB)
        self.enter_pw_textfield = Textfield(self.PASSWORD_TEXTFIELD_BB)
        self.show_pw_button = ShowPasswordButton(self.SHOW_PW_BUTTON_BB)
        self.signup_button = Button(self.SIGNUP_BUTTON_BB, lambda: self.signup())
        self.login_button = Button(self.LOGIN_BUTTON_BB, lambda: self.login())

        self.buttons: List[Button] = [self.signup_button, self.login_button,self.show_pw_button]
        self.textfields: List[Textfield] = [self.enter_email_textfield, self.enter_pw_textfield]
        
        self.add_widget(self.enter_email_textfield)
        self.add_widget(self.enter_pw_textfield)
        self.add_widget(self.show_pw_button)
        print("SignupPage init")

    @property
    def reward_template(self):
        '''
        The reward template for the signup page. TODO: finish template
        '''
        return {

        }

    def render(self, img):
        """
        Renders the page onto the given image. 
        The image changes depending on the state of the page.

        args: img - the image to render onto
        returns: the rendered image
        """
    
        to_render = cv2.imread(self.IMG_PATH)
        
        if(textfield_check([self.enter_email_textfield])):
            to_render = combine_path_for_image("signup_page_img/signup_window_email.png")
        
        if(textfield_check([self.enter_pw_textfield])):
            to_render = combine_path_for_image("signup_page_img/signup_window_pw.png")

        if(textfield_check([self.enter_email_textfield, self.enter_pw_textfield])):
            to_render = combine_path_for_image("signup_page_img/signup_window_email_pw.png")

        if(textfield_check([self.enter_pw_textfield]) and self.show_pw_button.showing_password):
            to_render = combine_path_for_image("signup_page_img/signup_window_pwshown.png")

        if(textfield_check([self.enter_email_textfield, self.enter_pw_textfield]) and self.show_pw_button.showing_password):
            to_render = combine_path_for_image("signup_page_img/signup_window_email_pwshown.png")
        
        draw_rectangles_around_clickables([self.buttons, self.textfields], to_render)
               
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
        self.show_pw_button.showing_password = False
        
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
        
        for textfield in self.textfields:
            if textfield.is_clicked_by(click_position):
                textfield.handle_click(click_position)
                break
        
        

        
       
   
            
        
    