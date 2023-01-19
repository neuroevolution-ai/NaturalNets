import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown,DropdownItem
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki import DeckDatabase


class ExportDeckPage(Page,RewardElement):
    
    """
    State description:
            state[0]: if this window is open
    """
    
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "export_deck_page.png")
    
    WINDOW_BB = BoundingBox(100, 100, 380, 278)
    INCLUDE_DD_BB = BoundingBox(246, 145, 222, 24)
    HTML_CHECKBOX_BB = BoundingBox(113, 179, 16, 16)
    EXPORT_BB = BoundingBox(272, 339, 91, 26)
    CANCEL_BB = BoundingBox(374, 338, 91, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ExportDeckPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.deck_database = DeckDatabase()
        
        dropdown_items = []
        for deck in self.deck_database.decks:
            dropdown_items.append(DropdownItem(deck,deck.name))

        self.include_dropdown = Dropdown(self.INCLUDE_DD_BB, dropdown_items)
        self.export_button = Button(self.EXPORT_BB, self.export_deck)
        self.cancel_button = Button(self.CANCEL_BB, self.close)

        self.add_widget(self.include_dropdown)

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "exported": 0
        }
        
    def handle_click(self,click_position: np.ndarray):
        if (self.include_dropdown.is_open()):
            self.include_dropdown.handle_click(click_position)        
        else:
            if(self.export_button.is_clicked_by(click_position)):
                self.export_button.handle_click(click_position)
            elif(self.cancel_button.is_clicked_by(click_position)):
                self.cancel_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self):
        return self.get_state()[0]

    def export_deck(self):
        self.register_selected_reward(["exported"])
        self.deck_database.export_deck(self.include_dropdown.get_selected_item().get_value())

    def render(self,img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if (self.get_state()[1] == 1):
            img = self.include_dropdown.render(img)
        return img