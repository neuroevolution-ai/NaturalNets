import os
from typing import List

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
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
    IMG_PATH = os.path.join(IMAGES_PATH, "search_page_img\search_page.png")
    SEARCH_TEXTFIELD_BB = BoundingBox(280, 23, 1350, 75)
    SHOW_ALL_BUTTON_BB = BoundingBox(1630, 23, 120, 75)

    TEST1_BUTTON_BB = BoundingBox(145, 135, 150, 60)
    TEST2_BUTTON_BB = BoundingBox(145, 220, 150, 60)
    TEST3_BUTTON_BB = BoundingBox(145, 305, 150, 60)

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

        self.search_textfield = Textfield(self.SEARCH_TEXTFIELD_BB)
        self.show_all_button = ShowPasswordButton(
            self.SHOW_ALL_BUTTON_BB, lambda: self.reset_search_text())
        self.test1_button = ShowPasswordButton(self.TEST1_BUTTON_BB)
        self.test2_button = ShowPasswordButton(self.TEST2_BUTTON_BB)
        self.test3_button = ShowPasswordButton(self.TEST3_BUTTON_BB)

        self.test1_copy_button = Button(
            self.TEST1_COPY_BB, lambda: self.copy_password())
        self.test2_copy_button = Button(
            self.TEST2_COPY_BB, lambda: self.copy_password())
        self.test3_copy_button = Button(
            self.TEST3_COPY_BB, lambda: self.copy_password())

        self.edit_popup = SearchEditPopUp()
        self.test1_edit_button = Button(
            self.TEST1_EDIT_BB, lambda: self.edit_popup.open_popup())
        self.test2_edit_button = Button(
            self.TEST2_EDIT_BB, lambda: self.edit_popup.open_popup())
        self.test3_edit_button = Button(
            self.TEST3_EDIT_BB, lambda: self.edit_popup.open_popup())

        self.test1_delete_button = Button(
            self.TEST1_DELETE_BB, lambda: self.delete_password())
        self.test2_delete_button = Button(
            self.TEST2_DELETE_BB, lambda: self.delete_password())
        self.test3_delete_button = Button(
            self.TEST3_DELETE_BB, lambda: self.delete_password())

        self.widgets: List[Widget] = [self.search_textfield, self.show_all_button, self.test1_button, self.test2_button, self.test3_button,
                                      self.test1_copy_button, self.test2_copy_button, self.test3_copy_button,
                                      self.test1_edit_button, self.test2_edit_button, self.test3_edit_button,
                                      self.test1_delete_button, self.test2_delete_button, self.test3_delete_button]

        self.buttons: List[Widget] = [self.show_all_button, self.test1_button, self.test2_button, self.test3_button,
                                      self.test1_copy_button, self.test2_copy_button, self.test3_copy_button,
                                      self.test1_edit_button, self.test2_edit_button, self.test3_edit_button,
                                      self.test1_delete_button, self.test2_delete_button, self.test3_delete_button]

        self.textfields: List[Widget] = [self.search_textfield]

        self.textsearchwidgets: List[Widget] = [
            self.search_textfield, self.show_all_button]
        self.password_buttons: List[Widget] = [
            self.test1_button, self.test2_button, self.test3_button]
      
        self.set_reward_children([self.edit_popup])
        self.add_child(self.edit_popup)
        self.add_widget(self.search_textfield)
        self.add_widget(self.show_all_button)
        print("SearchPage created")

    @property
    def reward_template(self):
        '''
        Returns the reward template for the page.
        '''
        return {

        }

    def reset(self):
        '''
        Resets the page to its default state.
        '''
        self.search_textfield.set_selected(False)
        self.show_all_button.showing_password = False
        self.test1_button.showing_password = False
        self.test2_button.showing_password = False
        self.test3_button.showing_password = False
        self.edit_popup.reset()
        
    def reset_search_text(self):
        '''
        Resets the search textfield to its default state.
        '''
        self.search_textfield.set_selected(False)

    def close_other_passwords(self, password_button):
        '''
        Closes all other password buttons except the given one.
        '''
        for button in self.password_buttons:
            if button != password_button:
                button.showing_password = False

    def render(self, img):
        """
        Renders the page onto the given image. 
        The image changes depending on the state of the page.

        args: img - the image to render onto
        returns: the rendered image
        """
        state = (
            textfield_check([self.search_textfield]),
            self.test1_button.is_password_shown(),
            self.test2_button.is_password_shown(),
            self.test3_button.is_password_shown(),
            self.show_all_button.is_password_shown()
        )

        img_paths = {
            (True, False, False, False, False): os.path.join(IMAGES_PATH, "search_page_img\search_page_searchtype.png"),
            (True, True, False, False, False): os.path.join(IMAGES_PATH, "search_page_img\search_page_searchdone_option1.png"),
            (False, False, False, False, True): os.path.join(IMAGES_PATH, "search_page_img\search_page_searchdone.png"),
            (False, True, False, False, True): os.path.join(IMAGES_PATH, "search_page_img\search_page_option1.png"),
            (False, False, True, False, True): os.path.join(IMAGES_PATH, "search_page_img\search_page_option2.png"),
            (False, False, False, True, True): os.path.join(IMAGES_PATH, "search_page_img\search_page_option3.png"),
        }

        to_render = cv2.imread(img_paths.get(state, self.IMG_PATH))

        if (self.is_popup_open()):
            to_render = self.get_open_popup().render(to_render)

        draw_rectangles_around_clickables(
            [self.buttons, self.textfields], to_render)

        img = to_render
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
                widget.handle_click(click_position)
                break

        if (self.show_all_button.is_password_shown() or self.search_textfield.is_selected()):
            self.handle_password_click(click_position)
            return

    def handle_password_click(self, click_position: np.ndarray):
        '''
        Handles clicks on the indvidudal password buttons.
        '''
        for button in self.password_buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)
                self.close_other_passwords(button)

        specific_buttons = []
        if self.test1_button.is_password_shown():
            specific_buttons += [self.test1_copy_button,
                                 self.test1_edit_button, self.test1_delete_button]
        if self.test2_button.is_password_shown():
            specific_buttons += [self.test2_copy_button,
                                 self.test2_edit_button, self.test2_delete_button]
        if self.test3_button.is_password_shown():
            specific_buttons += [self.test3_copy_button,
                                 self.test3_edit_button, self.test3_delete_button]

        for button in specific_buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)
                break

    def is_popup_open(self):
        '''
        Returns true if a popup is open.
        returns: bool
        '''
        if (self.edit_popup.is_open()):
            return True
        return False

    def get_open_popup(self):
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
        print("copy password")
        pass

    def delete_password(self):
        '''
        Method for deleting the password.
        '''
        print("delete password")
        pass

class SearchEditPopUp(PopUp):
    """Popup for the calculator settings (pops up when no operator-checkbox is selected).

       State description:
            state[0]: the opened-state of this popup.
    """
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
        self.BOUNDING_BOX = BoundingBox(650, 305, 615, 395)
        self.IMG_PATH = os.path.join(
            IMAGES_PATH, "settings_page_img\settings_page_colour_popup.png")
        print("SearchEditPopUp created")

