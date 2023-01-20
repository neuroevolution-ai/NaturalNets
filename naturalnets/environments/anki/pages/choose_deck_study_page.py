from math import floor
import os
import cv2
import numpy as np
from naturalnets.environments.anki.pages.main_page_popups import AddDeckPopup
from naturalnets.environments.anki import DeckDatabase
from naturalnets.environments.anki.pages.main_page_popups.leads_to_external_website_popup import LeadsToExternalWebsitePopup
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.widgets.button import Button

class ChooseDeckStudyPage(Page,RewardElement):

    """
    State description:
            state[0]: if this window is open
            state[i]: i-th menu item of the profiles bounding-box (6 > i > 0)
    """

    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "choose_deck_study_page.png")
    
    WINDOW_BB = BoundingBox(150, 150, 498, 374)
    STUDY_BB = BoundingBox(204, 476, 111, 31)
    ADD_BB = BoundingBox(293, 476, 87, 31)
    CANCEL_BB = BoundingBox(405, 476, 111, 31)
    HELP_BB = BoundingBox(534, 476, 95, 31)

    DECK_BB = BoundingBox(194, 210, 407, 145)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ChooseDeckStudyPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.leads_to_external_website_popup = LeadsToExternalWebsitePopup()
        self.add_deck_popup = AddDeckPopup()
        self.add_child(self.add_deck_popup)        
        self.add_child(self.leads_to_external_website_popup)
        self.current_index: int = 0
        
        self.deck_database = DeckDatabase()
        self.add_button: Button = Button(self.ADD_BB, self.add_deck_popup.open)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)
        self.help_button: Button = Button(self.HELP_BB, self.help)
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2, 3, 4],
            "help": 0,
            "study": 0
        }        
    
    def open(self):
        self.current_index = 0
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])
    
    def help(self):
        self.leads_to_external_website_popup.open()
        self.register_selected_reward(["help"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (469,22)
        # Box containing the items has size (471,280)
        # Top left corner (13,45)
        current_bounding_box = self.calculate_current_bounding_box()
        if(current_bounding_box.is_point_inside(click_point)):
            click_index: int = floor((click_point[1]- 210) / 29)
            print(click_index)
            self.current_index: int = click_index
            self.register_selected_reward(["index", self.current_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (194, 210)
       length = 29 * self.deck_database.decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 407, length)
       return current_bounding_box
    
    def reset_index(self):
        self.current_index: int = 0
    
    def render(self,img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img,f"{self.deck_database.decks[self.current_index].name}", (181, 194), font_scale = 0.5)
        # Items have size (469,22)
        if(self.leads_to_external_website_popup.is_open()):
            self.leads_to_external_website_popup.render(img)
        elif(self.add_deck_popup.is_open()):
            self.add_deck_popup.render(img)
        for i, deck in enumerate (self.deck_database.decks):
            if((self.add_deck_popup.is_open() and i >= 1) or (self.leads_to_external_website_popup.is_open() and i >= 3)):
                continue
            put_text(img, f" {deck.name}", (200, 231 + 29 * i), font_scale = 0.5)
        return img

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.leads_to_external_website_popup.is_open()):
            self.leads_to_external_website_popup.handle_click(click_position)
            return
        if(self.add_deck_popup.is_open()):
            self.add_deck_popup.handle_click(click_position)
            return
        elif(self.add_button.is_clicked_by(click_position)):
            self.add_button.handle_click(click_position)
        elif(self.cancel_button.is_clicked_by(click_position)):
            self.cancel_button.handle_click(click_position)
        elif(self.help_button.is_clicked_by(click_position)):
            self.help_button.handle_click(click_position)
        elif(self.calculate_current_bounding_box().is_point_inside(click_position)):
            self.change_current_deck_index(click_position)
        
