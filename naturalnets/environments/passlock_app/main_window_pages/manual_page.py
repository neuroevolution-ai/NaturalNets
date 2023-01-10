
from typing import List
import os
import cv2
import numpy as np
from naturalnets.environments.gui_app import widgets
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup
from naturalnets.environments.passlock_app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.passlock_app.utils import draw_rectangle_from_bb


class ManualPage(Page, RewardElement):

    STATE_LEN = 0
    offsetBB = 150
    NAME_OF_PW_TEXTFIELD_BB = BoundingBox(130+offsetBB, 230, 1479, 75)
    PASSWORD_TEXTFIELD_BB = BoundingBox(130+offsetBB, 380, 1479-75, 75)
    CREATE_PW_BB = BoundingBox(130+offsetBB, 492, 1479, 74)
    SHOW_PW_BB = BoundingBox(130+1479+offsetBB-75, 380, 75, 75)
    IMG_PATH = os.path.join(IMAGES_PATH, "home_window.png")

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)
   
        self.enter_nameof_password_radiobutton = RadioButton(self.NAME_OF_PW_TEXTFIELD_BB, None, lambda: self.enter_nameof_password())
 
        self.enter_secret_password_radiobutton = RadioButton(
            self.PASSWORD_TEXTFIELD_BB,
            None,
            lambda: self.enter_secret_password()
        )

        self.is_password_visible = 0
        self.show_password_radiobutton = RadioButton(
            self.SHOW_PW_BB,
            None,
            lambda: self.show_password()
        )

        self.create_pw_button = Button(self.CREATE_PW_BB, lambda: self.create_pw())
        
        self.radio_button_group = RadioButtonGroup(
            [self.enter_nameof_password_radiobutton, self.enter_secret_password_radiobutton, self.show_password_radiobutton]
        )

        self.buttons: List[Button] = [self.create_pw_button]
        self.widgets: List[Widget] = [self.radio_button_group, self.create_pw_button]
        self.add_widget(self.radio_button_group)
        
        
    @property
    def reward_template(self):
        return {

        }
    
    def reset(self):
        self.enter_nameof_password_radiobutton.set_selected(False)
        self.enter_secret_password_radiobutton.set_selected(False)
        self.show_password_radiobutton.set_selected(False)

    def handle_click(self, click_position: np.ndarray):
        '''
        This function is called when the user clicks on the signup page. 
        If the user clicks on a button, the button's function is called.

        args: click_position: the position of the click
        '''
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)
                    
        self.radio_button_group.handle_click(click_position)   

    
    def render(self, img: np.ndarray):
        """
        Renders the page onto the given image. 
        The image changes depending on the state of the page.

        args: img - the image to render onto
        returns: the rendered image
        """

        to_render = cv2.imread(self.IMG_PATH)

        if(self.enter_nameof_password_radiobutton.is_selected()):
            path = os.path.join(IMAGES_PATH, "manual_page_img\manual_page_nopw.png")
            to_render = cv2.imread(path)

        if(self.enter_secret_password_radiobutton.is_selected()):
            path = os.path.join(IMAGES_PATH, "manual_page_img\manual_page_pw.png")
            to_render = cv2.imread(path)
          
        if(self.enter_nameof_password_radiobutton.is_selected() and self.enter_secret_password_radiobutton.is_selected()):
            path = os.path.join(IMAGES_PATH, "manual_page_img\manual_page_nopw_pw.png")
            to_render = cv2.imread(path)

        if(self.enter_secret_password_radiobutton.is_selected()  
            and self.show_password_radiobutton.is_selected()):
            path = os.path.join(IMAGES_PATH, "manual_page_img\manual_page_pwshown.png")
            to_render = cv2.imread(path)

        if(self.enter_nameof_password_radiobutton.is_selected() 
            and self.enter_secret_password_radiobutton.is_selected() 
            and self.show_password_radiobutton.is_selected()):
            path = os.path.join(IMAGES_PATH, "manual_page_img\manual_page_nopw_pwshwon.png")
            to_render = cv2.imread(path)
   
        for button in self.buttons:
            draw_rectangle_from_bb(to_render, button._bounding_box, (0, 255, 0), 2)

        for rbg in self.radio_button_group.radio_buttons:
            draw_rectangle_from_bb(to_render, rbg._bounding_box, (0, 255, 0), 2)

        img = to_render
        return img
    
    def enter_nameof_password(self):
        '''
        This function is called when the user clicks on the enter name of password radio button.
        '''
        if(self.enter_nameof_password_radiobutton.is_selected()):
            self.enter_nameof_password_radiobutton.set_selected(False)
        else:
            self.enter_nameof_password_radiobutton.set_selected(True)
        

    def enter_secret_password(self):
        '''
        This function is called when the user clicks on the enter secret password radio button.
        '''
        if(self.enter_secret_password_radiobutton.is_selected()):
            self.enter_secret_password_radiobutton.set_selected(False)
        else:
            self.enter_secret_password_radiobutton.set_selected(True)

    def show_password(self):
        '''
        This function is called when the user clicks on the show password radio button.
        '''
        if(self.show_password_radiobutton.is_selected()):
            self.show_password_radiobutton.set_selected(False)
        else:
            self.show_password_radiobutton.set_selected(True)
        

    def create_pw(self):
        if(self.enter_nameof_password_radiobutton.is_selected() and self.enter_secret_password_radiobutton.is_selected()):
            self.reset()