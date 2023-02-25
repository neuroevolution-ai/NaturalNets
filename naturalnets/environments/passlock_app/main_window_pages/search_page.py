import logging
import os
from typing import List, Optional

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import ORANGE_COLOR
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.widgets.button import (
    Button, ShowPasswordButton)
from naturalnets.environments.passlock_app.constants import (IMAGES_PATH,
                                                             WINDOW_AREA_BB)
from naturalnets.environments.passlock_app.utils import (
    draw_rectangles_around_clickables, textfield_check)
from naturalnets.environments.passlock_app.widgets.popup import PopUp
from naturalnets.environments.passlock_app.widgets.textfield import Textfield


class SearchPage(Page, RewardElement):
    '''
    The search page of the Passlock app.

    State Description:
        The Search Page has no state itself, but it has a state for each of its widgets with a inherent state.
        0: Search textfield is selected.
        1: Show all button is selected.
        2: Test1 button is selected.
        3: Test2 button is selected.
        4: Test3 button is selected.
        5: Test1 copy button is selected.
        6: Test2 copy button is selected.
        7: Test3 copy button is selected.
        8: Test1 edit button is selected.
        9: Test2 edit button is selected.
        10: Test3 edit button is selected.
        11: Test1 delete button is selected.
        12: Test2 delete button is selected.
        13: Test3 delete button is selected.
    '''

    ### Constants###
    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "search_page_img", "search_page.png")
    SEARCH_TEXTFIELD_BB = BoundingBox(280, 23, 1350, 75)
    SHOW_ALL_BUTTON_BB = BoundingBox(1630, 23, 120, 75)

    ORIGINAL_TEST1_BUTTON_BB = BoundingBox(145, 135, 1350, 60)
    ORIGINAL_TEST2_BUTTON_BB = BoundingBox(145, 220, 1350, 60)
    ORIGINAL_TEST3_BUTTON_BB = BoundingBox(145, 305, 1350, 60)

    MODIFIED_TEST2_BUTTON_BB = BoundingBox(145, 270, 1350, 60)
    MODIFIED_TEST3_BUTTON_BB = BoundingBox(145, 350, 1350, 60)

    TEST1_COPY_BB = BoundingBox(1668, 192, 50, 50)
    TEST2_COPY_BB = BoundingBox(1668, 280, 50, 50)
    TEST3_COPY_BB = BoundingBox(1668, 365, 50, 50)

    TEST1_EDIT_BB = BoundingBox(1738, 192, 50, 50)
    TEST2_EDIT_BB = BoundingBox(1738, 280, 50, 50)
    TEST3_EDIT_BB = BoundingBox(1738, 365, 50, 50)

    TEST1_DELETE_BB = BoundingBox(1808, 192, 50, 50)
    TEST2_DELETE_BB = BoundingBox(1808, 280, 50, 50)
    TEST3_DELETE_BB = BoundingBox(1808, 365, 50, 50)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, WINDOW_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.search_textfield = Textfield(self.SEARCH_TEXTFIELD_BB, lambda: self.reset_show_all(), ORANGE_COLOR)
        self.show_all_button = ShowPasswordButton(self.SHOW_ALL_BUTTON_BB, lambda: self.reset_search_text(), ORANGE_COLOR)
        
        self.test1_button = ShowPasswordButton(self.ORIGINAL_TEST1_BUTTON_BB)
        self.test2_button = ShowPasswordButton(self.ORIGINAL_TEST2_BUTTON_BB)
        self.test3_button = ShowPasswordButton(self.ORIGINAL_TEST3_BUTTON_BB)

        self.test1_copy_button = Button(
            self.TEST1_COPY_BB, lambda: self.copy_password)
        self.test2_copy_button = Button(
            self.TEST2_COPY_BB, lambda: self.copy_password)
        self.test3_copy_button = Button(
            self.TEST3_COPY_BB, lambda: self.copy_password)

        self.edit_popup = SearchEditPopUp()
        self.test1_edit_button = Button(
            self.TEST1_EDIT_BB, lambda: self.edit_popup.open_popup())
        self.test2_edit_button = Button(
            self.TEST2_EDIT_BB, lambda: self.edit_popup.open_popup())
        self.test3_edit_button = Button(
            self.TEST3_EDIT_BB, lambda: self.edit_popup.open_popup())

        self.test1_delete_button = Button(
            self.TEST1_DELETE_BB, lambda: self.delete_password)
        self.test2_delete_button = Button(
            self.TEST2_DELETE_BB, lambda: self.delete_password)
        self.test3_delete_button = Button(
            self.TEST3_DELETE_BB, lambda: self.delete_password)

        self.buttons: List[Widget] = [self.show_all_button, self.test1_button, self.test2_button, self.test3_button,
                                      self.test1_copy_button, self.test2_copy_button, self.test3_copy_button,
                                      self.test1_edit_button, self.test2_edit_button, self.test3_edit_button,
                                      self.test1_delete_button, self.test2_delete_button, self.test3_delete_button]

        self.textfields: List[Widget] = [self.search_textfield]

        self.textsearchwidgets: List[Widget] = [
            self.search_textfield, self.show_all_button]
        self.password_buttons: List[Widget] = [
            self.test1_button, self.test2_button, self.test3_button]

        self.reward_widgets_to_str = {
            self.search_textfield: "search_textfield",
            self.show_all_button: "show_all_button",
            self.test1_button: "test1_button",
            self.test2_button: "test2_button",
            self.test3_button: "test3_button",
        }

        self.set_reward_children([self.edit_popup])
        self.add_child(self.edit_popup)

        self.add_widget(self.show_all_button)
        self.add_widget(self.test1_button)
        self.add_widget(self.test2_button)
        self.add_widget(self.test3_button)
        self.add_widget(self.search_textfield)
        
        logging.debug("SearchPage created")

    @property
    def reward_template(self):
        '''
        Returns the reward template for the page.
        '''
        return {
            "search_textfield": [False, True],
            "show_all_button": [False, True],
            "test1_button": [False, True],
            "test2_button": [False, True],
            "test3_button": [False, True]
        }

    def reset(self):
        '''
        Resets the page to its default state.
        '''
        self.search_textfield.reset()
        self.show_all_button.reset()
        self.test1_button.reset()
        self.test2_button.reset
        self.test3_button.reset()
        self.edit_popup.reset()

    def reset_search_text(self):
        '''
        Resets the search textfield to its default state.
        '''
        self.search_textfield.set_selected(False)
        self.test1_button.showing_password = False
        self.test2_button.showing_password = False
        self.test3_button.showing_password = False

    def reset_show_all(self):
        '''
        Resets the show all button to its default state.
        '''
        self.show_all_button.showing_password = False
        self.test1_button.showing_password = False
        self.test2_button.showing_password = False
        self.test3_button.showing_password = False
        

    def close_other_passwords(self, password_button):
        '''
        Closes all other password buttons except the given one.
        '''
        for button in self.password_buttons:
            if button != password_button:
                button.showing_password = False
        
        self.test1_button._bounding_box = self.ORIGINAL_TEST1_BUTTON_BB
        self.test2_button._bounding_box = self.ORIGINAL_TEST2_BUTTON_BB
        self.test3_button._bounding_box = self.ORIGINAL_TEST3_BUTTON_BB

  
    def render(self, img: np.ndarray)-> np.ndarray:
        """
        Renders the page onto the given image. 
        The image changes depending on the state of the page.

        args: img - the image to render onto
        returns: the rendered image
        """
  
        if (self.is_popup_open()):
            img = self.get_open_popup().render(img)
            return img
        
        state = (
            textfield_check([self.search_textfield]),
            self.test1_button.is_selected(),
            self.test2_button.is_selected(),
            self.test3_button.is_selected(),
            self.show_all_button.is_selected()
        )

        if self.test1_button.is_selected():
            self.test2_button._bounding_box = self.MODIFIED_TEST2_BUTTON_BB
            self.test3_button._bounding_box = self.MODIFIED_TEST3_BUTTON_BB
        
        if self.test2_button.is_selected():
            self.test3_button._bounding_box = self.MODIFIED_TEST3_BUTTON_BB

        img_paths = {
            (True, False, False, False, False): os.path.join(IMAGES_PATH, "search_page_img", "search_page_searchtype.png"),
            (True, True, False, False, False): os.path.join(IMAGES_PATH, "search_page_img", "search_page_searchdone_option1.png"),                                             
            (False, False, False, False, True): os.path.join(IMAGES_PATH, "search_page_img", "search_page_searchdone.png"),
            (False, True, False, False, True): os.path.join(IMAGES_PATH, "search_page_img", "search_page_option1.png"),
            (False, False, True, False, True): os.path.join(IMAGES_PATH, "search_page_img", "search_page_option2.png"),
            (False, False, False, True, True): os.path.join(IMAGES_PATH, "search_page_img", "search_page_option3.png"),
        }

        img_path = img_paths.get(state, self.IMG_PATH)
        self.set_image_path(img_path)
        img = super().render(img)

        return img

    def handle_click(self, click_position: np.ndarray):
        '''
        Handles clicks on the page.

        args: click_position - the position of the click
        '''

        if (self.is_popup_open()):
            self.get_open_popup().handle_click(click_position)
            return

        for widget in self.textsearchwidgets:
            if widget.is_clicked_by(click_position):
                # If the clickable has a selected state, register the reward when it is selected
                if (isinstance(widget, StateElement)):
                    self.register_selected_reward(
                        [self.reward_widgets_to_str[widget], widget.is_selected()])   
                                 
                widget.handle_click(click_position)
                break

        if (self.show_all_button.is_selected() or self.search_textfield.is_selected()):
            self.handle_all_password_click(click_position)
            return

    def handle_all_password_click(self, click_position: np.ndarray):
        '''
        Handles clicks on the individual password buttons.
        '''
        for button in self.password_buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)
                self.close_other_passwords(button)

        specific_buttons = []
        for i in range(1, 4):
            if getattr(self, f"test{i}_button").is_selected():
                specific_buttons += [
                    getattr(self, f"test{i}_copy_button"),
                    getattr(self, f"test{i}_edit_button"),
                    getattr(self, f"test{i}_delete_button")
                ]

        for button in specific_buttons:
            if button.is_clicked_by(click_position):

                if (isinstance(button, StateElement)):
                    self.register_selected_reward(
                        [self.reward_widgets_to_str[button], button.is_selected()])       

                button.handle_click(click_position)
                break

    def is_popup_open(self) -> bool:
        '''
        Returns true if a popup is open.
        returns: bool
        '''
        if (self.edit_popup.is_open()):
            return True
        return False

    def get_open_popup(self) -> Optional[PopUp]:
        '''
        Returns the open popup.
        returns: Popup
        '''
        if self.edit_popup.is_open():
            return self.edit_popup

    def copy_password(self):
        '''
        Method for copying the password.
        '''
        logging.debug("copy password")
        

    def delete_password(self):
        '''
        Method for deleting the password.
        '''
        logging.debug("delete password")
        


class SearchEditPopUp(PopUp):
    """Popup for the Editing passwords on the search page. Pops up when the edit button is clicked.

       State description:
            state[0]: the opened-state of this popup.
    """
    IMG_PATH = os.path.join(
                IMAGES_PATH, "search_page_img", "search_page_editpopup.png")
    BOUNDING_BOX = BoundingBox(650, 305, 615, 395)
    def __init__(self):
        super().__init__(WINDOW_AREA_BB, self.IMG_PATH)
        logging.debug("SearchEditPopUp created")
