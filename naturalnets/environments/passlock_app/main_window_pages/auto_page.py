from typing import List
import os
import cv2
import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup
from naturalnets.environments.passlock_app.constants import IMAGES_PATH, WINDOW_AREA_BB
from naturalnets.environments.passlock_app.utils import combine_path_for_image, draw_rectangles_around_clickables, textfield_check
from naturalnets.environments.passlock_app.widgets.slider import Slider
from naturalnets.environments.passlock_app.widgets.textfield import Textfield


class AutoPage(Page, RewardElement):

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "auto_page_img\\auto_page.png")
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
        Page.__init__(self, self.STATE_LEN, WINDOW_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.enter_nameof_password_textfield = Textfield(self.NAME_OF_PW_TEXTFIELD_BB)
        self.enter_password_textfield = Textfield(self.PASSWORD_TEXTFIELD_BB)

        self.copy_pw_button = Button(self.COPY_PW_BB, lambda: self.copy_password())
        self.reset_pw_button = Button(self.RESET_PW_BB, lambda: self.reset_password())
        self.create_pw_button = Button(self.GENERATE_PW_BB, lambda: self.generate_password())
        self.pw_length_slider = Slider(self.PW_LENGTH_BB, 3)
        self.pw_length_slider.set_slider_value(0)

        self.use_letters_checkbox = CheckBox(self.USE_LETTERS_BB)
        self.use_numbers_checkbox = CheckBox(self.USE_NUMBERS_BB)
        self.use_special_chars_checkbox = CheckBox(self.USE_SPECIAL_CHARS_BB)

        self.sliders: List[Slider] = [self.pw_length_slider]
        self.checkboxes: List[CheckBox] = [self.use_letters_checkbox, self.use_numbers_checkbox, self.use_special_chars_checkbox]
        self.textfields: List[Textfield] = [self.enter_nameof_password_textfield, self.enter_password_textfield]	
        self.buttons: List[Button] = [self.copy_pw_button, self.reset_pw_button, self.create_pw_button]
        self.widgets: List[Widget] = [self.use_letters_checkbox, self.use_numbers_checkbox, self.use_special_chars_checkbox]
        self.clickables = self.sliders + self.checkboxes + self.textfields + self.buttons

        self.add_widget(self.pw_length_slider)
        self.add_widget(self.use_letters_checkbox)
        self.add_widget(self.use_numbers_checkbox)
        self.add_widget(self.use_special_chars_checkbox)
        self.add_widget(self.enter_nameof_password_textfield)
        self.add_widget(self.enter_password_textfield)

        print("AutoPage created")

    @property
    def reward_template(self):
        return {

        }

    def render(self, img):
        """
        Renders the page onto the given image. 
        The image changes depending on the state of the page.

        args: img - the image to render onto
        returns: the rendered image
        """

        state = (
            self.pw_length_slider.get_slider_value(), 
            self.use_letters_checkbox.is_selected(), 
            self.use_numbers_checkbox.is_selected(), 
            self.use_special_chars_checkbox.is_selected(), 
            textfield_check([self.enter_nameof_password_textfield]), 
            textfield_check([self.enter_password_textfield])
            )
        
        img_paths = {
            (1, 0, 0, 0, False, False): os.path.join(IMAGES_PATH, "auto_page_img\\auto_page_slidermiddle.png"),
            (2, 0, 0, 0, False, False): os.path.join(IMAGES_PATH, "auto_page_img\\auto_page_sliderend.png"),
            (0, 1, 0, 0, False, False): os.path.join(IMAGES_PATH, "auto_page_img\\auto_page_pw_cb1.png"),
            (0, 1, 1, 0, False, False): os.path.join(IMAGES_PATH, "auto_page_img\\auto_page_pw_cb2.png"),
            (0, 1, 1, 1, False, False): os.path.join(IMAGES_PATH, "auto_page_img\\auto_page_pw_cb3.png"),
            (0, 0, 0, 0, True, False): os.path.join(IMAGES_PATH, "auto_page_img\\auto_page_namepw.png"),
            (0, 0, 0, 0, False, True): os.path.join(IMAGES_PATH, "auto_page_img\\auto_page_pw.png"),
            (0, 0, 0, 0, True, True): os.path.join(IMAGES_PATH, "auto_page_img\\auto_page_namepw_pw.png"),
        }

        to_render = cv2.imread(img_paths.get(state, self.IMG_PATH))
        draw_rectangles_around_clickables([self.clickables], to_render)
        img = to_render
        return img

    def reset(self):
        self.enter_nameof_password_textfield.reset()
        self.enter_password_textfield.reset()

    def handle_click(self, click_position: np.ndarray):
        '''
        Handles a click on the page.

        args: click_position - the position of the click
        '''
      
        for clickable in self.clickables:
            if clickable.is_clicked_by(click_position):
                clickable.handle_click(click_position)
                break

    def copy_password(self):
        print("copied password")
        pass 

    def reset_password(self):
        self.enter_password_textfield.reset()

    def generate_password(self):
        self.reset()
