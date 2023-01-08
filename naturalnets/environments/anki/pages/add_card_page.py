import os
import random
import string

import numpy as np
from choose_deck_page import ChooseDeckPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki.deck import DeckDatabase
from naturalnets.environments.anki.card import Card
class AddCardPage(Page,RewardElement):
    """
    STATE_LEN is composed of (the opened state of the page, if the front field is filled,
        if the back field is filled, if the tags field is filled)
    """
    
    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "add_card.png")

    WINDOW_BB = BoundingBox(0, 0, 568, 494)
    SELECT_BB = BoundingBox(328, 48, 223, 26)
    FRONT_TEXT_BB = BoundingBox(456, 216, 91, 26)
    BACK_TEXT_BB = BoundingBox(456, 294, 91, 26)
    TAGS_TEXT_BB = BoundingBox(463, 418, 87, 21)
    CLOSE_BB = BoundingBox(358, 453, 91, 26)
    ADD_BB = BoundingBox(157, 453, 91, 26)
    CLOSE_WINDOW_BB = BoundingBox(507, 0, 61, 38)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AddCardPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        
        self.secure_random = random.SystemRandom() 
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.front_side_clipboard_temporary_string = None
        self.back_side_clipboard_temporary_string = None
        self.tag_clipboard_temporary_string = None
        
        self.choose_deck = ChooseDeckPage()
        self.add_child(self.choose_deck)
               
        self.select_button: Button = Button(self.SELECT_BB, self.choose_deck.open())
        self.front_text_button: Button = Button(self.FRONT_TEXT_BB, self.set_front_side_clipboard())
        self.back_text_button: Button = Button(self.BACK_TEXT_BB, self.set_back_side_clipboard())
        self.tags_text_button: Button = Button(self.TAGS_TEXT_BB, self.set_tag_clipboard())
        self.close_button: Button = Button(self.CLOSE_BB, self.close())
        self.add_button: Button = Button(self.ADD_BB, self.add_card())
        self.close_window_button: Button = Button(self.CLOSE_WINDOW_BB, self.close())
        
        self.add_widgets([self.select_button,self.front_text_button,self.back_text_button,self.tags_text_button
            ,self.close_button,self.add_button,self.close_window_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "front_side_clipboard": "clicked",
            "back_side_clipboard": "clicked",
            "tag_clipboard": "clicked"
        }
    
    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.select_button.is_clicked_by(click_position)):
            self.select_button.handle_click(click_position)
        elif(self.front_text_button.is_clicked_by(click_position)):
            self.front_text_button.handle_click(click_position)
        elif(self.back_text_button.is_clicked_by(click_position)):
            self.back_text_button.handle_click(click_position)
        elif(self.tags_text_button.is_clicked_by(click_position)):
            self.tags_text_button.handle_click(click_position)
        elif(self.close_button.is_clicked_by(click_position)):
            self.close_button.handle_click(click_position)
        elif(self.add_button.is_clicked_by(click_position)):
            self.add_button.handle_click(click_position)
        elif(self.close_window_button.is_clicked_by(click_position)):
            self.close_window_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
        self.reset_temporary_strings()

    def is_open(self):
        return self.get_state()[0]
    
    def set_front_side_clipboard(self):
        self.register_selected_reward(["front_side_clipboard","clicked"])
        self.front_side_clipboard_temporary_string = self.secure_random.choices(string.ascii_lowercase + string.digits, 10)
        self.get_state()[1] = 1
    
    def set_back_side_clipboard(self):
        self.register_selected_reward(["back_side_clipboard","clicked"])
        self.back_side_clipboard_temporary_string = self.secure_random.choices(string.ascii_lowercase + string.digits, 10)
        self.get_state()[2] = 1

    def set_tag_clipboard(self):
        self.register_selected_reward(["tag_clipboard","clicked"])
        self.tag_clipboard_temporary_string = self.secure_random.choices(string.ascii_lowercase + string.digits, 10)
        self.get_state()[3] = 1

    def is_card_creatable(self):
        return self.back_side_clipboard_temporary_string is not None and self.front_side_clipboard_temporary_string is not None
    
    def reset_temporary_strings(self):
        self.back_side_clipboard_temporary_string = None
        self.front_side_clipboard_temporary_string = None
        self.tag_clipboard_temporary_string = None

    def add_card(self):
        if(self.is_card_creatable()):
            card = Card(self.front_side_clipboard_temporary_string,self.back_side_clipboard_temporary_string)
            card.tag = self.tag_clipboard_temporary_string
            DeckDatabase().current_deck.add_card(card)
