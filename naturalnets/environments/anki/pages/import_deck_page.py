from math import floor
import os
import numpy as np
from naturalnets.environments.anki import NameExistsPopupPage
from naturalnets.environments.anki.pages.main_page_popups import FiveDecksPopupPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH, PREDEFINED_DECKS_PATH
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.anki import DeckDatabase, Deck
from naturalnets.environments.gui_app.utils import put_text

class ImportDeckPage(Page,RewardElement):
    """
    State description:
            state[0]: if this window is open
    """
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "import_deck_page.png")

    WINDOW_BB = BoundingBox(20, 20, 689, 584)
    SELECT_DECK_BB = BoundingBox(405, 62, 277, 27)
    HTML_BB = BoundingBox(44, 169, 16, 16)
    IMPORT_BB = BoundingBox(402, 562, 92, 27)
    CLOSE_BB = BoundingBox(504, 562, 92, 27)
    HELP_BB = BoundingBox(604, 562, 92, 27)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ImportDeckPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.import_deck_popup = ImportDeckPopupPage()
        self.name_exists_popup = NameExistsPopupPage()
        self.five_decks_popup = FiveDecksPopupPage()
        self.add_children([self.import_deck_popup, self.name_exists_popup, self.five_decks_popup])

        self.current_deck: Deck = None

        self.select_deck_button = Button(self.SELECT_DECK_BB, self.import_deck_popup.open)
        self.html_checkbox = CheckBox(self.HTML_BB, self.html_click)
        self.import_button = Button(self.IMPORT_BB, self.import_deck)
        self.close_button = Button(self.CLOSE_BB, self.close)
        self.help_button = Button(self.HELP_BB, self.help)
    
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
        self.import_deck_popup.open()
    
    def html_click(self):
        if(self.html_checkbox.get_state()):
            self.register_selected_reward(["checkbox","true"])
        else:
            self.register_selected_reward(["checkbox","false"])
    
    def import_deck(self):
        if (self.current_deck is None):
            return
        elif (not(DeckDatabase().is_deck_length_allowed())):
            self.five_decks_popup.open()
            return
        elif (DeckDatabase().is_included(DeckDatabase().deck_import_names[self.import_deck_popup.current_index])):
            self.name_exists_popup.open()
            return
        else:
            DeckDatabase().import_deck(self.current_deck.name)
            self.close()
    
    def render(self,img: np.ndarray):
        img = super().render(img)
        if (self.import_deck_popup.get_state()[0]):
            img = self.import_deck_popup.render(img)
        elif (self.five_decks_popup.get_state()[0]):
            img = self.five_decks_popup.render(img)
        elif (self.name_exists_popup.get_state()[0]):
            img = self.name_exists_popup.render(img)
        return img

class ImportDeckPopupPage(Page,RewardElement):
    """
    State description:
            state[0]: if this window is open
            state[i]: if the i-th item is selected i = {1,2,3}
    """
    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "import_deck_popup.png")

    WINDOW_BB = BoundingBox(100, 100, 499, 373)
    CHOOSE_BB = BoundingBox(290, 434, 91, 27)
    HELP_BB = BoundingBox(494, 434, 91, 27)
    DECK_BB = BoundingBox(113, 145, 472, 280)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ImportDeckPopupPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.current_index: int = 0

        self.choose_button: Button = Button(self.CHOOSE_BB, self.choose_deck)
        self.help_button: Button = Button(self.HELP_BB, self.help)
        self.add_widgets([self.choose_button, self.help_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2, 3, 4],
            "help": 0,
        }
    
    def handle_click(self,click_position: np.ndarray):
        if(self.choose_button.is_clicked_by(click_position)):
            self.choose_button.handle_click(click_position)
        elif(self.help_button.is_clicked_by(click_position)):
            self.help_button.handle_click(click_position)
            
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])
    
    def help(self):
        print("Led to external website")
        self.register_selected_reward(["help"])
    
    def is_open(self) -> int:
        return self.get_state()[0]

    def change_current_deck_index(self,click_point: np.ndarray):
        # Items have size (469,22)
        # Box containing the items has size (472,280)
        # Top left corner (13,45)
        current_bounding_box = self.calculate_current_bounding_box()
        if(current_bounding_box.is_point_inside(click_point)):
            click_index: int = floor((click_point[1] - 145)/22)
            self.current_index: int = click_index
            self.register_selected_reward(["index", click_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (115,145)
       length = 22 * DeckDatabase().count_number_of_files(PREDEFINED_DECKS_PATH)
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 472, length)
       return current_bounding_box
    
    def choose_deck(self):
        ImportDeckPage().current_deck = Deck(DeckDatabase().deck_import_names[self.current_index])

    def render(self,img: np.ndarray):
        img = super().render(img)
        for i, deck_name in enumerate (DeckDatabase().deck_import_names):
            put_text(img, f"{deck_name}", (115, 145 + (22 * (i + 1))), font_scale = 0.3)
        return img