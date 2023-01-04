from ast import List

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup


class SearchPage(Page, RewardElement):

    STATE_LEN = 0

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
        Page.__init__(self)
        RewardElement.__init__(self)

        self._bounding_box = self.APP_BOUNDING_BOX

        self.search_textfield = RadioButton(self.SEARCH_TEXTFIELD_BB, self.enter_search_text())
        self.show_all_button = Button(self.SHOW_ALL_BUTTON_BB)
        self.test1_button = Button(self.TEST1_BUTTON_BB)
        self.test2_button = Button(self.TEST2_BUTTON_BB)
        self.test3_button = Button(self.TEST3_BUTTON_BB)

        self.test1_copy_button = Button(self.TEST1_COPY_BB)
        self.test2_copy_button = Button(self.TEST2_COPY_BB)
        self.test3_copy_button = Button(self.TEST3_COPY_BB)

        self.test1_edit_button = Button(self.TEST1_EDIT_BB)
        self.test2_edit_button = Button(self.TEST2_EDIT_BB)
        self.test3_edit_button = Button(self.TEST3_EDIT_BB)

        self.test1_delete_button = Button(self.TEST1_DELETE_BB)
        self.test2_delete_button = Button(self.TEST2_DELETE_BB)
        self.test3_delete_button = Button(self.TEST3_DELETE_BB)

        self.radio_button_group = RadioButtonGroup(self.SEARCH_TEXTFIELD_BB)

        self.widgets: List[Widget] = [self.search_textfield, self.show_all_button, self.test1_button, self.test2_button, self.test3_button,
                                      self.test1_copy_button, self.test2_copy_button, self.test3_copy_button,
                                      self.test1_edit_button, self.test2_edit_button, self.test3_edit_button,
                                      self.test1_delete_button, self.test2_delete_button, self.test3_delete_button]

        self.add_widgets(self.widgets) 

    def enter_search_text(self):
        pass

    def reset():
        pass

    def render():
        pass
    
    def handle_click(self, click_position: np.ndarray):
        pass
