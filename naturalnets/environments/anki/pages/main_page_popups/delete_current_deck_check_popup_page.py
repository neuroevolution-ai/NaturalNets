import os
import cv2

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.deck import DeckDatabase
from naturalnets.environments.anki.pages.main_page_popups.at_least_one_deck_popup_page import AtLeastOneDeckPopupPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button


class DeleteCurrentDeckPopupPage(Page,RewardElement):
    
    """
    State description:
        state[0]: if this window is open  
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "delete_current_deck_check.png")
    
    WINDOW_BB = BoundingBox(130, 270, 530, 113)
    YES_BB = BoundingBox(394, 347, 77, 26)
    NO_BB = BoundingBox(476, 346, 77, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeleteCurrentDeckPopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.deck_database = DeckDatabase()
        
        self.yes_button = Button(self.YES_BB,self.remove_deck)
        self.no_button = Button(self.NO_BB,self.close)
        
        self.add_widget([self.yes_button, self.no_button])
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.yes_button.is_clicked_by(click_position)):
            self.yes_button.handle_click(click_position)
        elif(self.no_button.is_clicked_by(click_position)):
            self.no_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]

    def remove_deck(self):
        self.deck_database.delete_deck(self.deck_database.current_deck.name)
        self.close()

    def render(self,img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img