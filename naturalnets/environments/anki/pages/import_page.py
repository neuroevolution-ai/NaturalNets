import os

import numpy as np
from choose_deck_page import ChooseDeckPage
from name_exists_popup_page import NameExistsPopupPage
from five_decks_popup_page import FiveDecksPopupPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.anki.deck import DeckDatabase, Deck
class ImportPage(Page,RewardElement):
    """
    STATE_LEN is composed of if this window is open, 
    if choose deck is open and if the checkbox is selected
    """
    STATE_LEN = 3
    IMG_PATH = os.path.join(IMAGES_PATH, "import_page.png")

    WINDOW_BB = BoundingBox(0,0,689,620)
    SELECT_DECK_BB = BoundingBox(386,79,277,27)
    HTML_BB = BoundingBox(25,185,16,16)
    IMPORT_BB = BoundingBox(382,579,92,27)
    CLOSE_BB = BoundingBox(484,579,92,27)
    HELP_BB = BoundingBox(584,579,92,27)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ImportPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.choose_deck_page = ChooseDeckPage()
        self.name_exists_popup = NameExistsPopupPage()
        self.five_decks_popup = FiveDecksPopupPage()

        self.current_deck: Deck = None

        self.select_deck_button = Button(self.SELECT_DECK_BB, self.choose_deck_page.open())
        self.html_checkbox = CheckBox(self.HTML_BB, self.html_click())
        self.import_button = Button(self.IMPORT_BB, self.import_deck())
        self.close_button = Button(self.CLOSE_BB, self.close())
        self.help_button = Button(self.HELP_BB, self.help())
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "checkbox": ["true", "false"],
            "help": "clicked",
            "deck": "open"
        }
    
    def handle_click(self, click_position: np.ndarray) -> None:
        if (self.select_deck_button.is_clicked_by(click_position)):
            self.select_deck_button.handle_click(click_position)
        elif (self.html_checkbox.is_clicked_by(click_position)):
            self.html_checkbox.handle_click(click_position)
        elif (self.import_button.is_clicked_by(click_position)):
            self.import_button.handle_click(click_position)
        elif (self.close_button.is_clicked_by(click_position)):
            self.close_button.handle_click(click_position)
        elif (self.help_button.is_clicked_by(click_position)):
            self.help_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]
    
    def help(self):
        print("Led to external website")
        self.register_selected_reward(["help","clicked"])

    def choose_deck(self):
        self.register_selected_reward(["deck","open"])
        self.choose_deck_page.open()
    
    def html_click(self):
        if(self.html_checkbox.get_state()):
            self.register_selected_reward(["checkbox","true"])
        else:
            self.register_selected_reward(["checkbox","false"])
    
    def import_deck(self):
        if(DeckDatabase().is_deck_length_allowed()):
            self.five_decks_popup.open()
            return
        elif(DeckDatabase().is_included(DeckDatabase().deck_import_names[self.choose_deck_page.current_index])):
            self.name_exists_popup.open()
            return
        else:
            DeckDatabase().import_deck(self.current_deck.name)
            self.close()