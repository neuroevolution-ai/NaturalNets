import os
import random
from five_decks_popup_page import FiveDecksPopupPage
from name_exists_popup_page import NameExistsPopupPage
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki.deck import DeckDatabase
class AddDeckPopupPage(Page,RewardElement):
    """
    STATE_LEN is composed of the information if this window is open and if the text field is filled 
    """
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "add_deck_popup.png")
    
    WINDOW_BB = BoundingBox(0, 0, 500, 147)
    OK_BB = BoundingBox(293, 106, 91, 26)
    TEXT_BB = BoundingBox(400, 74, 86, 22)
    CANCEL_BB = BoundingBox(394, 106, 92, 27)
    CLOSE_WINDOW_BB = BoundingBox(459, 0, 41, 37)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AddDeckPopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.five_decks_popup = FiveDecksPopupPage()
        self.name_exists_popup = NameExistsPopupPage()
        
        self.add_child(self.five_decks_popup)
        self.add_child(self.name_exists_popup)

        self.secure_random = random.SystemRandom()
        self.current_field_string = None
        
        self.ok_button: Button = Button(self.OK_BB, self.add_deck())
        self.text_button: Button = Button(self.TEXT_BB, self.set_deck_name_clipboard())
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close())
        self.close_window_button: Button = Button(self.CLOSE_WINDOW_BB, self.close())


    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "deck_name_clipboard": "clicked"
        }

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
        self.current_field_string = None
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def set_deck_name_clipboard(self):
        self.current_field_string = self.secure_random.random(DeckDatabase().deck_names)
        self.register_selected_reward(["deck_name_clipboard","clicked"])

    def add_deck(self):
        if(not(DeckDatabase().is_deck_length_allowed())):
            self.five_decks_popup.open()
        elif(DeckDatabase().is_included(self.current_field_string)):
            self.name_exists_popup.open()
        elif(self.current_field_string is not None):
            DeckDatabase().create_deck(self.current_field_string)