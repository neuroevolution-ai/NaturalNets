import os
from naturalnets.environments.anki.deck import Deck
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki.deck import DeckDatabase


class ExportPage(Page,RewardElement):
    
    """
    STATE_LEN is composed of 5 bits for 5 decks and 1 for checkbox and 1 whether this window is open
    """
    
    STATE_LEN = 7
    IMG_PATH = os.path.join(IMAGES_PATH, "export_page.png")
    
    WINDOW_BB = BoundingBox(0, 0, 382, 317)
    INCLUDE_DD_BB = BoundingBox(146, 83, 222, 24)
    HTML_CHECKBOX_BB = BoundingBox(14, 117, 16, 16)
    EXPORT_BB = BoundingBox(174, 276, 91, 26)
    CANCEL_BB = BoundingBox(276, 276, 91, 26)
    CLOSE_WINDOW_BB = BoundingBox(325, 0, 57, 39)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ExportPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.current_deck: Deck = None
        self.include_dropdown = Dropdown(self.INCLUDE_DD_BB,[])
        self.html_checkbox = CheckBox(self.HTML_CHECKBOX_BB, lambda x : x)
        self.export_button = Button(self.EXPORT_BB, DeckDatabase().export_deck(self.current_deck))
        self.cancel_button = Button(self.CANCEL_BB, self.close())
        self.close_window_button = Button(self.CLOSE_WINDOW_BB, self.close())

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
        }

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]
