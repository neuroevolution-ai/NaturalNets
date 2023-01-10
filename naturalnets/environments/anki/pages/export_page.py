import os

import numpy as np
from naturalnets.environments.anki.deck import Deck
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown,DropdownItem
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki.deck import DeckDatabase


class ExportPage(Page,RewardElement):
    
    """
    STATE_LEN is composed of 2 bits. One whether the window is open and one whether the dropdown is open 
    """
    
    STATE_LEN = 2
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
        
        dropdown_items = []
        for deck in DeckDatabase().decks:
            dropdown_items.append(DropdownItem(deck,deck.name))

        self.include_dropdown = Dropdown(self.INCLUDE_DD_BB, dropdown_items)
        self.html_checkbox = CheckBox(self.HTML_CHECKBOX_BB)
        self.export_button = Button(self.EXPORT_BB, self.export_deck())
        self.cancel_button = Button(self.CANCEL_BB, self.close())
        self.close_window_button = Button(self.CLOSE_WINDOW_BB, self.close())

        self.add_widgets([self.include_dropdown,self.html_checkbox,self.export_button,
            self.cancel_button,self.close_window_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "exported": "true"
        }
 
    def handle_click(self,click_position: np.ndarray):
        if(self.include_dropdown.is_clicked_by(click_position)):
            self.include_dropdown.handle_click(click_position)
        elif(self.html_checkbox.is_clicked_by(click_position)):
            self.html_checkbox.handle_click(click_position)
        elif(self.export_button.is_clicked_by(click_position)):
            self.export_button.handle_click(click_position)
        elif(self.cancel_button.is_clicked_by(click_position)):
            self.cancel_button.handle_click(click_position)
        elif(self.close_window_button.is_clicked_by(click_position)):
            self.close_window_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]

    def reset_current_deck(self):
        self.include_dropdown.set_selected_item(self.include_dropdown.get_all_items())

    def export_deck(self):
        self.register_selected_reward(["exported","true"])
        DeckDatabase().export_deck(self.include_dropdown.get_selected_item().get_value())
