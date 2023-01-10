from typing import List
import os

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup
from naturalnets.environments.passlock_app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB


class SearchPage(Page, RewardElement):

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "search_window.png")
    SEARCH_TEXTFIELD_BB = BoundingBox(9, 28, 99, 22)
    SHOW_ALL_BUTTON_BB = BoundingBox(9, 52, 99, 22)
    TEST1_BUTTON_BB = BoundingBox(9, 76, 99, 22)
    TEST2_BUTTON_BB = BoundingBox(9, 76, 99, 22)
    TEST3_BUTTON_BB = BoundingBox(9, 76, 99, 22)

    TEST1_COPY_BB = BoundingBox(9, 76, 99, 22)
    TEST2_COPY_BB = BoundingBox(9, 76, 99, 22)
    TEST3_COPY_BB = BoundingBox(9, 76, 99, 22)

    TEST1_EDIT_BB = BoundingBox(9, 76, 99, 22)
    TEST2_EDIT_BB = BoundingBox(9, 76, 99, 22)
    TEST3_EDIT_BB = BoundingBox(9, 76, 99, 22)

    TEST1_DELETE_BB = BoundingBox(9, 76, 99, 22)
    TEST2_DELETE_BB = BoundingBox(9, 76, 99, 22)
    TEST3_DELETE_BB = BoundingBox(9, 76, 99, 22)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.search_textfield = RadioButton(self.SEARCH_TEXTFIELD_BB, lambda: self.enter_search_text())
        self.show_all_button = Button(self.SHOW_ALL_BUTTON_BB, lambda: self.nothing())
        self.test1_button = Button(self.TEST1_BUTTON_BB, lambda: self.nothing())
        self.test2_button = Button(self.TEST2_BUTTON_BB, lambda: self.nothing())
        self.test3_button = Button(self.TEST3_BUTTON_BB, lambda: self.nothing())

        self.test1_copy_button = Button(self.TEST1_COPY_BB, lambda: self.nothing())
        self.test2_copy_button = Button(self.TEST2_COPY_BB, lambda: self.nothing())
        self.test3_copy_button = Button(self.TEST3_COPY_BB, lambda: self.nothing())

        self.test1_edit_button = Button(self.TEST1_EDIT_BB, lambda: self.nothing())
        self.test2_edit_button = Button(self.TEST2_EDIT_BB, lambda: self.nothing())
        self.test3_edit_button = Button(self.TEST3_EDIT_BB, lambda: self.nothing())

        self.test1_delete_button = Button(self.TEST1_DELETE_BB, lambda: self.nothing())
        self.test2_delete_button = Button(self.TEST2_DELETE_BB, lambda: self.nothing())
        self.test3_delete_button = Button(self.TEST3_DELETE_BB, lambda: self.nothing())

        self.radio_button_group = RadioButtonGroup([self.search_textfield])

        self.widgets: List[Widget] = [self.search_textfield, self.show_all_button, self.test1_button, self.test2_button, self.test3_button,
                                      self.test1_copy_button, self.test2_copy_button, self.test3_copy_button,
                                      self.test1_edit_button, self.test2_edit_button, self.test3_edit_button,
                                      self.test1_delete_button, self.test2_delete_button, self.test3_delete_button]

        #self.add_widget(self.show_all_button)
        #self.add_widget(self.test1_button)
        #self.add_widget(self.test2_button)
        #self.add_widget(self.test3_button)
        #self.add_widget(self.test1_copy_button)
        #self.add_widget(self.test2_copy_button)
        #self.add_widget(self.test3_copy_button)
        #self.add_widget(self.test1_edit_button)
        #self.add_widget(self.test2_edit_button)
        #self.add_widget(self.test3_edit_button)
        #self.add_widget(self.test1_delete_button)
        #self.add_widget(self.test2_delete_button)
        #self.add_widget(self.test3_delete_button)
        self.add_widget(self.radio_button_group)
        print("SearchPage created")

    @property
    def reward_template(self):
        return {

        }
    	
    def reset():
        pass
    
    def enter_search_text(self):
        pass

    def render():
        pass
    
    def handle_click(self, click_position: np.ndarray):
        pass

    def nothing(self):
        pass 
