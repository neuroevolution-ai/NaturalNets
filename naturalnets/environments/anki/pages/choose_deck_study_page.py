from math import floor
import os
import numpy as np
from naturalnets.environments.anki.pages.main_page_popups import AddDeckPopupPage
from naturalnets.environments.anki import DeckDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import put_text
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.widgets.button import Button

class ChooseDeckStudyPage(Page,RewardElement):

    """
    State description:
            state[0]: if this window is open
            state[i]: i-th menu item of the profiles bounding-box (6 > i > 0)
    """

    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "choose_deck_study.png")
    
    WINDOW_BB = BoundingBox(20, 20, 498, 374)
    STUDY_BB = BoundingBox(111, 354, 91, 26)
    ADD_BB = BoundingBox(212, 354, 91, 26)
    CANCEL_BB = BoundingBox(313, 354, 91, 26)
    HELP_BB = BoundingBox(415, 354, 91, 26)

    DECK_BB = BoundingBox(33, 65 ,471 ,280)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ChooseDeckStudyPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.add_deck_popup = AddDeckPopupPage()
        self.add_child(self.add_deck_popup)        
        
        self.current_index: int = 0

        self.study_button: Button = Button(self.STUDY_BB, self.study_deck)
        self.add_button: Button = Button(self.ADD_BB,self.add_deck_popup.open)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)
        self.help_button: Button = Button(self.HELP_BB, self.help)

        self.add_widgets([self.study_button,self.add_button,self.cancel_button,self.help_button])
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2, 3, 4],
            "help": 0,
            "study": 0,
        }
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def help(self):
        print("Led to external website")
        self.register_selected_reward(["help"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (469,22)
        # Box containing the items has size (471,280)
        # Top left corner (13,45)
        current_bounding_box = self.calculate_current_bounding_box()
        if(current_bounding_box.is_point_inside(click_point)):
            click_index: int = floor((click_point[1]- 65)/22)
            self.current_index: int = click_index
            self.register_selected_reward(["index", self.current_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (33,65)
       length = 22 * DeckDatabase().decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 471, length)
       return current_bounding_box

    def study_deck(self):
        if(self.current_index is not None):
            DeckDatabase().set_current_deck(DeckDatabase().decks[self.current_index])
            self.register_selected_reward(["study"])
            self.close()
    
    def reset_index(self):
        self.current_index: int = 0
    
    def render(self,img: np.ndarray):
        img = super().render(img)
        # Items have size (469,22)
        for i, deck in enumerate (DeckDatabase().decks):
            put_text(img, f" {deck.name}", (36, 65 + 22 * (i + 1)),font_scale = 0.3)
        return img

    def handle_click(self, click_position: np.ndarray) -> None:
        "return super().handle_click(click_position)"