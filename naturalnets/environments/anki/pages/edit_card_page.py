import os

import numpy as np
from naturalnets.environments.anki.card import Card
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki.deck import DeckDatabase

class EditCardPage(RewardElement,Page):
    
    """
    STATE_LEN is determined by if this window is open
    """

    IMG_PATH = os.path.join(IMAGES_PATH, "edit_card.png")
    STATE_LEN = 1

    WINDOW_BB = BoundingBox(50, 50, 499, 500)
    FRONT_TEXT_BB = BoundingBox(437, 201, 91, 27)
    BACK_TEXT_BB = BoundingBox(438, 277, 91, 27)
    TAGS_TEXT_BB = BoundingBox(441, 473, 88, 22)
    CLOSE_BB = BoundingBox(442, 508, 91, 27)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EditCardPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.front_text_button: Button = Button(self.FRONT_TEXT_BB,self.front_text_edit())
        self.back_text_button: Button = Button(self.BACK_TEXT_BB,self.back_text_edit())
        self.tags_text_button: Button = Button(self.TAGS_TEXT_BB,self.tags_text_edit())
        self.close_button: Button = Button(self.CLOSE_BB,self.close())

        self.add_widgets([self.front_text_button,self.back_text_button,
            self.tags_text_button,self.close_button])

    def handle_click(self, click_position: np.ndarray):
        if self.front_text_button.is_clicked_by(click_position):
            self.front_text_button.handle_click(click_position)
        elif self.back_text_button.is_clicked_by(click_position):
            self.back_text_button.handle_click(click_position)
        elif self.tags_text_button.is_clicked_by(click_position):
            self.tags_text_button.handle_click(click_position)
        elif self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "first_field_modified": 0,
            "second_field_modified": 0,
            "tags_field_modified": 0
        }

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]
    
    def front_text_edit(self):
        if(not(DeckDatabase().current_deck.current_card.is_front_edited())):
            DeckDatabase().current_deck.current_card.edit_front()
            self.register_selected_reward(["first_field_modified"])
    
    def back_text_edit(self):
        if(not(DeckDatabase().current_deck.current_card.is_back_edited())):
            DeckDatabase().current_deck.current_card.edit_back()
            self.register_selected_reward(["second_field_modified"])
        
    def tags_text_edit(self):
        if(not(DeckDatabase().current_deck.current_card.is_tag_edited())):
            DeckDatabase().current_deck.current_card.edit_tag()
            self.register_selected_reward(["tags_field_modified"])
