import os
import random
import cv2
import numpy as np
from naturalnets.environments.anki.pages.main_page_popups.five_decks_popup import FiveDecksPopup
from naturalnets.environments.anki.pages.name_exists_popup import NameExistsPopup
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki import DeckDatabase
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button

class AddDeckPopup(Page,RewardElement):
    """
    State description:
            state[0]: if this popup is open
            state[1]: if the text field is filled
    """
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "add_deck_popup.png")
    
    WINDOW_BB = BoundingBox(150, 250, 498, 109)
    OK_BB = BoundingBox(443, 324, 81, 25)
    CANCEL_BB = BoundingBox(538, 324, 103, 25)
    TEXT_BB = BoundingBox(555, 289, 86, 20)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AddDeckPopup, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.five_decks_popup = FiveDecksPopup()
        self.name_exists_popup = NameExistsPopup()
        self.profile_database = ProfileDatabase()
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        
        self.add_child(self.five_decks_popup)
        self.add_child(self.name_exists_popup)

        self.secure_random = random.SystemRandom()
        self.current_field_string = None
        
        self.ok_button: Button = Button(self.OK_BB, self.add_deck)
        self.text_button: Button = Button(self.TEXT_BB, self.set_deck_name_clipboard)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)

        self.set_reward_children([self.name_exists_popup, self.five_decks_popup])
    
    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "set_clipboard": 0,
            "add_new_deck": 0
        }

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0

    def open(self):
        self.register_selected_reward(["window", "open"])
        self.get_state()[0] = 1

    def set_deck_name_clipboard(self):
        self.register_selected_reward(["set_clipboard"])
        self.current_field_string = self.secure_random.choice(self.deck_database.deck_names)

    def is_open(self):
        return self.get_state()[0]
    
    def add_deck(self):
        if (self.current_field_string is None):
            return
        elif (not(self.deck_database.is_deck_length_allowed())):
            self.five_decks_popup.open()
        elif (self.deck_database.is_included(self.current_field_string)):
            self.name_exists_popup.open()
        else:
            self.deck_database.create_deck(self.current_field_string)
            self.register_selected_reward(["add_new_deck"])
            self.current_field_string = None
            self.close()
    
    def render(self,img: np.ndarray):
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if(self.current_field_string is not None):
            put_text(img, f"{self.current_field_string}", (181, 302) ,font_scale = 0.4)
        if (self.five_decks_popup.is_open()):
            img = self.five_decks_popup.render(img)
        elif (self.name_exists_popup.is_open()):
            img = self.name_exists_popup.render(img)
        return img

    def handle_click(self, click_position: np.ndarray) -> None:
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        if (self.five_decks_popup.is_open()):
           self.five_decks_popup.handle_click(click_position)
           return
        elif (self.name_exists_popup.is_open()):
            self.name_exists_popup.handle_click(click_position)
            return
        elif (self.ok_button.is_clicked_by(click_position)):
            self.ok_button.handle_click(click_position)
        elif (self.text_button.is_clicked_by(click_position)):
            self.text_button.handle_click(click_position)
        elif (self.cancel_button.is_clicked_by(click_position)):
            self.cancel_button.handle_click(click_position)