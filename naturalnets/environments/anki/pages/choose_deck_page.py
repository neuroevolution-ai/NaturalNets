from math import floor
import os
import cv2
import numpy as np
from naturalnets.environments.anki.pages.main_page_popups import AddDeckPopupPage
from naturalnets.environments.anki import DeckDatabase
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button

class ChooseDeckPage(Page,RewardElement):
    """
        State description:
            state[0]: if this window is open
            state[i]: i-th menu item of the profiles bounding-box (6 > i > 0)
    """
    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "choose_deck.png")

    WINDOW_BB = BoundingBox(160, 160, 498, 375)
    CHOOSE_BB = BoundingBox(297, 494, 77, 27)
    ADD_BB = BoundingBox(382, 494, 77, 27)
    CLOSE_BB = BoundingBox(471, 495, 77, 27)
    DECK_BB = BoundingBox(13, 65, 472, 280)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ChooseDeckPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.deck_database = DeckDatabase()
        self.add_deck_popup = AddDeckPopupPage()
        self.add_child(self.add_deck_popup)

        self.current_index: int = 0

        self.add_button: Button = Button(self.ADD_BB, self.add_deck_popup.open)
        self.choose_button: Button = Button(self.CHOOSE_BB, self.choose_deck)
        self.close_button: Button = Button(self.CLOSE_BB, self.close)
        
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2, 3, 4]
        }
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (469,22)
        # Box containing the items has size (472,280)
        # Top left corner (33,65)
        current_bounding_box = self.calculate_current_bounding_box()
        if((current_bounding_box.is_point_inside(click_point))):
            click_index: int = floor((click_point[1] - 206) / 30)
            self.current_index: int = click_index
            self.register_selected_reward(["index", self.current_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (146,206)
       length = 30 * self.deck_database.decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 398, length)
       return current_bounding_box

    def choose_deck(self):
        self.deck_database.set_current_index(self.current_index)
        self.deck_database.set_current_deck(self.deck_database.decks[self.current_index])
        for i in range(1,6):
            self.get_state()[i] = 0
        self.get_state()[self.current_index + 1] = 1
        self.close()

    def reset_index(self):
        self.current_index: int = 0
    
    def render(self,img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if(self.add_deck_popup.is_open()):
            img = self.add_deck_popup.render(img)
        put_text(img, f" {self.deck_database.decks[self.current_index].name}", (170, 190), font_scale = 0.5)
        for i, deck in enumerate (self.deck_database.decks):
            if(self.add_deck_popup.is_open() and i >= 3):
                return img
            put_text(img, f" {deck.name}", (170, 195 + 30 * (i + 1)), font_scale = 0.5)
        return img

    def handle_click(self, click_position: np.ndarray) -> None:
        if (self.add_deck_popup.is_open()):
            self.add_deck_popup.handle_click(click_position)
            return
        elif (self.add_button.is_clicked_by(click_position)):
            self.add_button.handle_click(click_position)
        elif (self.choose_button.is_clicked_by(click_position)):
            self.choose_button.handle_click(click_position)
        elif (self.close_button.is_clicked_by(click_position)):
            self.close_button.handle_click(click_position)
        elif (self.calculate_current_bounding_box().is_point_inside(click_position)):
            self.change_current_deck_index(click_position)
