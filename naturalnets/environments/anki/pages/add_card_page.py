import os
import random
import string
import cv2
import numpy as np
from naturalnets.environments.anki import ChooseDeckPage
from naturalnets.environments.anki.pages.main_page_popups.front_and_backside_popup import FrontAndBacksidePopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki import Card
class AddCardPage(Page,RewardElement):
    """
    State description:
            state[0]: if this window is open
            state[i]: if the i-th field is filled (4 > i > 0)
    """
    
    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "add_card_page.png")

    WINDOW_BB = BoundingBox(130, 120, 566, 456)
    SELECT_BB = BoundingBox(545, 151, 120, 25)
    FRONT_TEXT_BB = BoundingBox(588, 299, 87, 25)
    BACK_TEXT_BB = BoundingBox(588, 407, 87, 25)
    TAGS_TEXT_BB = BoundingBox(588, 494, 87, 25)
    CLOSE_BB = BoundingBox(582, 538, 88, 25)
    ADD_BB = BoundingBox(466, 538, 88, 25)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AddCardPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.front_side_clipboard_temporary_string = None
        self.back_side_clipboard_temporary_string = None
        self.tag_clipboard_temporary_string = None
        
        self.profile_database = ProfileDatabase()
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        self.choose_deck = ChooseDeckPage()
        self.front_and_backside_popup = FrontAndBacksidePopup()
        
        self.add_child(self.choose_deck)
        self.add_child(self.front_and_backside_popup)
               
        self.select_button: Button = Button(self.SELECT_BB, self.select_deck)
        self.front_text_button: Button = Button(self.FRONT_TEXT_BB, self.set_front_side_clipboard)
        self.back_text_button: Button = Button(self.BACK_TEXT_BB, self.set_back_side_clipboard)
        self.tags_text_button: Button = Button(self.TAGS_TEXT_BB, self.set_tag_clipboard)
        self.close_button: Button = Button(self.CLOSE_BB, self.close)
        self.add_button: Button = Button(self.ADD_BB, self.add_card)
        
        self.set_reward_children([self.choose_deck, self.front_and_backside_popup])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "front_side_clipboard": 0,
            "back_side_clipboard": 0,
            "tag_clipboard": 0,
            "add_card": 0
        }
    
    def handle_click(self, click_position: np.ndarray) -> None:
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        if(self.choose_deck.is_open()):
            self.choose_deck.handle_click(click_position)
            return
        if(self.front_and_backside_popup.is_open()):
            self.front_and_backside_popup.handle_click(click_position)
            return
        elif(self.select_button.is_clicked_by(click_position)):
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
        self.reset_temporary_strings()
        
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.reset_temporary_strings()
        self.register_selected_reward(["window","close"])
        self.get_state()[0] = 0

    def is_open(self):
        return self.get_state()[0]
    
    def set_front_side_clipboard(self):
        self.register_selected_reward(["front_side_clipboard"])
        self.front_side_clipboard_temporary_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self.get_state()[1] = 1
    
    def set_back_side_clipboard(self):
        self.register_selected_reward(["back_side_clipboard"])
        self.back_side_clipboard_temporary_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self.get_state()[2] = 1

    def set_tag_clipboard(self):
        self.register_selected_reward(["tag_clipboard"])
        self.tag_clipboard_temporary_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self.get_state()[3] = 1

    def is_card_creatable(self):
        return self.back_side_clipboard_temporary_string is not None and self.front_side_clipboard_temporary_string is not None
    
    def reset_temporary_strings(self):
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
            self.deck_database.decks[self.deck_database.current_index].add_card(card)
            self.register_selected_reward(["add_card"])
            self.reset_temporary_strings()
        else:
            self.front_and_backside_popup.open()

    def select_deck(self):
        self.choose_deck.reset_index()
        self.choose_deck.open()

    def render(self,img: np.ndarray):
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if (self.choose_deck.is_open()):
            self.choose_deck.render(img)
            return img
        put_text(img, f"{self.deck_database.decks[self.deck_database.current_index].name}", (277,191) ,font_scale = 0.5)
        if (self.front_and_backside_popup.is_open()):
            self.front_and_backside_popup.render(img)
            if (self.back_side_clipboard_temporary_string is not None):
                put_text(img, f"{self.back_side_clipboard_temporary_string}", (198, 422) ,font_scale = 0.5)
            if (self.tag_clipboard_temporary_string is not None):
                put_text(img, f"{self.tag_clipboard_temporary_string}", (198, 507) ,font_scale = 0.5)
            return img
        if (self.front_side_clipboard_temporary_string is not None):
            put_text(img, f"{self.front_side_clipboard_temporary_string}", (197, 310) ,font_scale = 0.5)
        if (self.back_side_clipboard_temporary_string is not None):
            put_text(img, f"{self.back_side_clipboard_temporary_string}", (198, 422) ,font_scale = 0.5)
        if (self.tag_clipboard_temporary_string is not None):
            put_text(img, f"{self.tag_clipboard_temporary_string}", (198, 507) ,font_scale = 0.5)
        return img