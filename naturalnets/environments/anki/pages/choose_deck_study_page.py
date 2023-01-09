import os

import numpy as np
from add_deck_popup_page import AddDeckPopupPage
from naturalnets.environments.anki.deck import DeckDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from study_window_page import StudyWindowPage
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.widgets.button import Button

class ChooseDeckStudyPage(Page,RewardElement):

    """
    STATE_LEN is composed of if this window is open and of the 5 indexes
    """

    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "choose_deck_study.png")
    
    WINDOW_BB = BoundingBox(0, 0, 501, 411)
    STUDY_BB = BoundingBox(91, 372, 91, 26)
    ADD_BB = BoundingBox(192, 372, 91, 26)
    CANCEL_BB = BoundingBox(293, 372, 91, 26)
    HELP_BB = BoundingBox(395, 372, 91, 26)
    CLOSE_BB = BoundingBox(459, 0, 42, 38)

    DECK_BB = BoundingBox(15, 82 ,472 ,110)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ChooseDeckStudyPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.add_deck_popup = AddDeckPopupPage()
        self.study_window_page = StudyWindowPage()
        
        self.add_child(self.add_deck_popup)        
        self.add_child(self.study_window_page)
        
        self.current_index: int = 0

        self.study_button: Button = Button(self.STUDY_BB, self.study_deck())
        self.add_button: Button = Button(self.ADD_BB,self.add_deck_popup.open())
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close())
        self.help_button: Button = Button(self.HELP_BB, self.help())
        self.close_button: Button = Button(self.CLOSE_BB, self.close())
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2, 3, 4],
            "help": "clicked"
        }
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def help(self):
        print("Led to external website")
        self.register_selected_reward(["help","clicked"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (469,22)
        # Box containing the items has size (472,110)
        # Top left corner (15,82)
        current_bounding_box = self.calculate_current_bounding_box()
        if(not(current_bounding_box.is_point_inside(click_point))):
            print("Point not inside the profiles bounding box")
            return
        else:
            click_index: int = click_point[1]/22
            self.current_index = click_index

    def calculate_current_bounding_box(self):
       upper_left_point = (15,82)
       length = 22 * DeckDatabase().decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 469, length)
       return current_bounding_box

    def study_deck(self):
        if(self.current_index is not None):
            DeckDatabase().current_deck = DeckDatabase().decks[self.current_index]
            self.study_window_page.open()
            self.close()
    
    def reset_index(self):
        self.current_index = 0