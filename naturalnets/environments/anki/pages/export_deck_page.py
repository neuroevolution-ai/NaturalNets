import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import EXPORTED_DECKS_PATH, IMAGES_PATH
from naturalnets.environments.anki.pages.main_page_popups.five_decks_popup import FiveDecksPopup
from naturalnets.environments.anki.pages.name_exists_popup import NameExistsPopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown,DropdownItem
from naturalnets.environments.gui_app.widgets.button import Button


class ExportDeckPage(Page,RewardElement):
    
    """
    State description:
            state[0]: if this window is open
    """
    
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "export_deck_page.png")
    
    WINDOW_BB = BoundingBox(210, 200, 380, 278)
    INCLUDE_DD_BB = BoundingBox(324, 250, 224, 24)
    INCLUDE_DD_BB_OFFSET = BoundingBox(324, 274, 224, 24)
    EXPORT_BB = BoundingBox(346, 443, 113, 29)
    CANCEL_BB = BoundingBox(470, 443, 113, 29)
    RESET_BB = BoundingBox(218, 441, 110, 29)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ExportDeckPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.profile_database = ProfileDatabase()
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database

        self.current_deck = None
        self.five_decks_popup = FiveDecksPopup()
        self.name_exists_popup = NameExistsPopup()
        
        self.dropdown_items = []
        self.initialise_dropdown()
        
        self.include_dropdown = Dropdown(self.INCLUDE_DD_BB_OFFSET, self.dropdown_items)
        self.export_button = Button(self.EXPORT_BB, self.export_deck)
        self.cancel_button = Button(self.CANCEL_BB, self.close)
        self.reset_exported_decks_button = Button(self.RESET_BB, self.reset_exported_decks)
        
        self.add_child(self.five_decks_popup)
        self.add_child(self.name_exists_popup)
        self.add_widget(self.include_dropdown)
        self.set_reward_children([self.five_decks_popup,self.name_exists_popup])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "dropdown":{
                "opened": 0,
                "selected": [0, 1, 2, 3, 4]
            },
            "exported": 0,
            "reset": 0
        }
        
    def handle_click(self,click_position: np.ndarray):
        if (self.include_dropdown.is_open()):
            self.include_dropdown.handle_click(click_position)
        if (self.name_exists_popup.is_open()):
            self.name_exists_popup.handle_click(click_position)
            return
        if (self.five_decks_popup.is_open()):
            self.five_decks_popup.handle_click(click_position)
            return       
        if self.include_dropdown.get_selected_item() is not None:
            self.current_deck = self.include_dropdown.get_selected_item().get_value().name
            self.register_selected_reward(["dropdown", "selected", self.include_dropdown.get_all_items().index(self.include_dropdown.get_selected_item())])
        if (self.INCLUDE_DD_BB.is_point_inside(click_position)):
            self.register_selected_reward(["dropdown","opened"])
            self.include_dropdown.open()
            return
        else:
            if (self.export_button.is_clicked_by(click_position)):
                self.export_button.handle_click(click_position)
            elif (self.cancel_button.is_clicked_by(click_position)):
                self.cancel_button.handle_click(click_position)
            elif (self.reset_exported_decks_button.is_clicked_by(click_position)):
                self.reset_exported_decks_button.handle_click(click_position)

    def open(self):
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        self.initialise_dropdown()
        self.current_deck = None
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0
        

    def is_open(self):
        return self.get_state()[0]

    def export_deck(self):
        self.register_selected_reward(["exported"])
        if (self.deck_database.count_number_of_files(EXPORTED_DECKS_PATH) == 5):
            self.five_decks_popup.open()
        elif(self.include_dropdown.get_selected_item() is None):
            return
        elif(self.deck_database.is_file_exist(self.include_dropdown.get_selected_item().get_value().name, EXPORTED_DECKS_PATH)):
            self.name_exists_popup.open()
        else:
            self.deck_database.export_deck(self.include_dropdown.get_selected_item().get_value())
            self.close()

    def render(self,img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img, "" if self.current_deck is None else f"{self.current_deck}", (331, 265), font_scale = 0.4)
        put_text(img, f"Number of exported decks: {self.deck_database.count_number_of_files(EXPORTED_DECKS_PATH)}", (260, 320), font_scale = 0.5)
        if(self.five_decks_popup.is_open()):
            img = self.five_decks_popup.render(img)
        if(self.name_exists_popup.is_open()):
            img = self.name_exists_popup.render(img)
        if (self.include_dropdown.is_open()):
            img = self.include_dropdown.render(img)
        return img

    def initialise_dropdown(self):
        self.dropdown_items = []
        for deck in self.deck_database.decks:
            self.dropdown_items.append(DropdownItem(deck,deck.name))
        self.include_dropdown = Dropdown(self.INCLUDE_DD_BB_OFFSET, self.dropdown_items)

    def reset_exported_decks(self):
        self.deck_database.reset_exported_decks()
        self.register_selected_reward(["reset"])