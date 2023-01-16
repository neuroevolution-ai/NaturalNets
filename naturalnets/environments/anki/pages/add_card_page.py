import os
import random
import string
import cv2
import numpy as np
from naturalnets.environments.anki import ChooseDeckPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki import DeckDatabase
from naturalnets.environments.anki import Card
class AddCardPage(Page,RewardElement):
    """
    State description:
            state[0]: if this window is open
            state[i]: if the i-th field is filled (4 > i > 0)
    """
    
    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "add_card.png")

    WINDOW_BB = BoundingBox(100, 100, 566, 456)
    SELECT_BB = BoundingBox(376, 60, 223, 26)
    FRONT_TEXT_BB = BoundingBox(470, 276, 77, 26)
    BACK_TEXT_BB = BoundingBox(470, 356, 77, 26)
    TAGS_TEXT_BB = BoundingBox(475, 479, 77, 21)
    CLOSE_BB = BoundingBox(390, 513, 77, 26)
    ADD_BB = BoundingBox(216, 513, 77, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AddCardPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.secure_random = random.SystemRandom()

        self.front_side_clipboard_temporary_string = None
        self.back_side_clipboard_temporary_string = None
        self.tag_clipboard_temporary_string = None
        
        self.choose_deck = ChooseDeckPage()
        self.add_child(self.choose_deck)
               
        self.select_button: Button = Button(self.SELECT_BB, self.select_deck)
        self.front_text_button: Button = Button(self.FRONT_TEXT_BB, self.set_front_side_clipboard)
        self.back_text_button: Button = Button(self.BACK_TEXT_BB, self.set_back_side_clipboard)
        self.tags_text_button: Button = Button(self.TAGS_TEXT_BB, self.set_tag_clipboard)
        self.close_button: Button = Button(self.CLOSE_BB, self.close)
        self.add_button: Button = Button(self.ADD_BB, self.add_card)
        
        self.add_widgets([self.select_button, self.front_text_button, self.back_text_button, self.tags_text_button
            ,self.close_button, self.add_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "front_side_clipboard": ["set","reset"],
            "back_side_clipboard": ["set","reset"],
            "tag_clipboard": ["set","reset"],
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
        self.register_selected_reward(["front_side_clipboard","set"])
        self.front_side_clipboard_temporary_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self.get_state()[1] = 1
    
    def set_back_side_clipboard(self):
        self.register_selected_reward(["back_side_clipboard","set"])
        self.back_side_clipboard_temporary_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self.get_state()[2] = 1

    def set_tag_clipboard(self):
        self.register_selected_reward(["tag_clipboard","set"])
        self.tag_clipboard_temporary_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self.get_state()[3] = 1

    def is_card_creatable(self):
        return self.back_side_clipboard_temporary_string is not None and self.front_side_clipboard_temporary_string is not None
    
    def reset_temporary_strings(self):
        if(self.back_side_clipboard_temporary_string is not None):
            self.register_selected_reward(["back_side_clipboard","reset"])
        if(self.front_side_clipboard_temporary_string is not None):
            self.register_selected_reward(["front_side_clipboard","reset"])
        if(self.tag_clipboard_temporary_string is not None):
            self.register_selected_reward(["tag_clipboard","reset"])
        self.back_side_clipboard_temporary_string = None
        self.front_side_clipboard_temporary_string = None
        self.tag_clipboard_temporary_string = None
        self.get_state()[1] = 0
        self.get_state()[2] = 0
        self.get_state()[3] = 0

    def add_card(self):
        if(self.is_card_creatable()):
            card = Card(self.front_side_clipboard_temporary_string, self.back_side_clipboard_temporary_string)
            card.tag = self.tag_clipboard_temporary_string
            DeckDatabase().decks[ChooseDeckPage().current_index].add_card(card)
            self.reset_temporary_strings()

    def select_deck(self):
        self.choose_deck.open()

    def render(self,img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if(self.choose_deck.is_open()):
            self.choose_deck.render()
            return img
        if (self.front_side_clipboard_temporary_string is not None):
            put_text(img, f"{self.front_side_clipboard_temporary_string}", (150, 280) ,font_scale = 0.5)
        if (self.back_side_clipboard_temporary_string is not None):
            put_text(img, f"{self.back_side_clipboard_temporary_string}", (150, 360) ,font_scale = 0.5)
        if (self.tag_clipboard_temporary_string is not None):
            put_text(img, f"{self.tag_clipboard_temporary_string}", (165, 493) ,font_scale = 0.5)
        return img