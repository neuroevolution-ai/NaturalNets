import os

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from anki.pages.edit_card_page import EditCardPage
from anki.pages.main_page import MainPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki.deck import DeckDatabase

class StudyPage(RewardElement,Page):
    """
    State description:
            state[0]: if this window is open
            state[1]: if the show answer button is clicked  
    """
    
    IMG_PATH = os.path.join(IMAGES_PATH, "study_page.png")
    
    STATE_LEN = 2
    WINDOW_BB = BoundingBox(0, 0, 831, 710)
    
    FILE_BB = BoundingBox(0, 2, 42, 23)
    EDIT_BB = BoundingBox(42, 2, 47, 23)
    TOOLS_BB = BoundingBox(89, 2, 53, 23)
    HELP_BB = BoundingBox(142, 2, 50, 23)

    ADD_CARD_BB = BoundingBox(268, 32, 82, 29)
    SYNC_BB = BoundingBox(519, 29, 54, 29)

    EDIT_BB = BoundingBox(10, 698, 100, 28)
    SHOW_ANSWER_NEXT_BB = BoundingBox(379, 696, 115, 31)
    REMOVE_BB = BoundingBox(764, 698, 100, 28)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.main_page = MainPage()
        self.edit_page = EditCardPage()
        self.deck_database = DeckDatabase()
        self.deck_database.current_deck.create_study()
        
        self.edit_button = Button(self.EDIT_BB, self.edit_page.open())
        self.show_answer_button = Button(self.SHOW_ANSWER_NEXT_BB, self.show_answer())
        self.remove_button = Button(self.REMOVE_BB, self.deck_database.current_deck.cards.remove(self.deck_database.current_deck[self.deck_database.current_deck.study_index]))
        self.next_button = Button(self.SHOW_ANSWER_NEXT_BB, self.next_card())

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StudyPage, cls).__new__(cls)
        return cls.instance

    @property
    def reward_template(self):
        return {
            "window": 0,
            "remove": 0,
            "show_answer": 0,
            "edit": 0,
            "next_card": 0
        }
    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.edit_button.is_clicked_by(click_position)):
            self.edit_button.handle_click(click_position)
        elif(self.show_answer_button.is_clicked_by(click_position)):
            self.show_answer_button.handle_click(click_position)
        elif(self.remove_button.is_clicked_by(click_position)):
            self.remove_button.handle_click(click_position)
        elif(self.next_button.is_clicked_by(click_position)):
            self.next_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def show_answer(self):
        self.get_state()[1] = 1
        self.register_selected_reward(["show_answer"])
    
    def next_card(self):
        self.get_state()[1] = 0
        self.register_selected_reward(["next_card"])
        self.deck_database.current_deck.increment_study_index()

    def render(self,img: np.ndarray):
        super().render(img)
        put_text(img, self.deck_database.current_deck[self.deck_database.current_deck.study_index], (340 ,120), font_scale = 0.3)
        if (self.get_state()[1] == 1):
            put_text(img, self.deck_database.current_deck[self.deck_database.current_deck.study_index], (340 ,160), font_scale = 0.3)
        if (self.edit_page.is_open()):
            self.edit_page.render()

        
