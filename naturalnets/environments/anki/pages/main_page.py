import os
from typing import List

import numpy as np
from add_card_page import AddCardPage
from anki_login_page import AnkiLoginPage
from main_page_popups.add_deck_popup_page import AddDeckPopupPage
from reset_collection_popup import ResetCollectionPopupPage
from naturalnets.environments.gui_app.widgets.button import Button
from study_page import StudyPage
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.utils import put_text
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem
from choose_deck_study_page import ChooseDeckStudyPage
from anki.pages.check_media_page import CheckMediaPage
from preferences_page import PreferencesPage
from pages.import_page import ImportPage
from profile_page import ProfilePage
from export_page import ExportPage
from naturalnets.environments.anki.deck import DeckDatabase
from about_page import AboutPage

class MainPage(Page,RewardElement):
    
    """
    State description:
            state[i]: if this window is open i = {0,1,2,3,4}
            state[j]: i-th item is selected j = {5,6,7,8}  
    """
    STATE_LEN = 9
    IMG_PATH = os.path.join(IMAGES_PATH, "main_page.png")

    WINDOW_BB = BoundingBox(0, 0, 831, 710)
    DECKS_BB = BoundingBox(141, 276, 458, 150)
    
    GET_SHARED_BB = BoundingBox(272, 660, 93, 27)
    CREATE_DECK_BB = BoundingBox(369, 660, 93, 27)
    IMPORT_FILE_BB = BoundingBox(473, 660, 93, 27)
    
    ADD_CARD_BB = BoundingBox(310, 28, 46, 29)
    SYNC_BB = BoundingBox(524, 28, 54, 29)
    
    FILE_DROPDOWN_BB = BoundingBox(0, 0, 43, 23)
    EDIT_DROPDOWN_BB = BoundingBox(43, 0, 47, 23)
    TOOLS_DROPDOWN_BB = BoundingBox(90, 0, 53, 23)
    HELP_DROPDOWN_BB = BoundingBox(143, 0, 52, 23)

    STUDY_BB = BoundingBox(505, 165, 92, 27)


    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MainPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.profile_page = ProfilePage()
        self.import_page = ImportPage()
        self.export_page = ExportPage()
        self.choose_deck_study_page = ChooseDeckStudyPage()
        self.check_media_page = CheckMediaPage()
        self.preferences_page = PreferencesPage()
        self.study_page = StudyPage()
        self.about_page = AboutPage()
        self.add_card_page = AddCardPage()
        self.anki_login = AnkiLoginPage()
        self.add_deck_popup_page = AddDeckPopupPage()

        self.add_children([self.profile_page,self.import_page,self.export_page,self.choose_deck_study_page,
        self.check_media_page,self.preferences_page,self.study_page,self.about_page,self.add_card_page,
        self.anki_login,self.add_deck_popup_page])

        switch_profile_ddi = DropdownItem(self.profile_page.open(), "Switch Profile")
        import_ddi = DropdownItem(self.import_page.open(), "Import")
        export_ddi = DropdownItem(self.export_page.open(), "Export")
        exit_ddi = DropdownItem(self.reset(), "Exit")

        self.study_deck_ddi = DropdownItem(self.choose_deck_study_page.open(), "Study Deck")
        self.check_media_ddi = DropdownItem(self.check_media_page.open(), "Check Media")
        self.preferences_ddi = DropdownItem(self.preferences_page.open(), "Preferences")

        self.guide_ddi = DropdownItem(None, "Guide")
        self.support_ddi = DropdownItem(None, "Support")
        self.about_ddi = DropdownItem(self.about_page.open(), "About Page")

        self.file_dropdown = Dropdown(self.FILE_DROPDOWN_BB,[switch_profile_ddi,import_ddi,export_ddi,exit_ddi])
        self.edit_dropdown = Dropdown(self.EDIT_DROPDOWN_BB,[])
        self.tools_dropdown = Dropdown(self.TOOLS_DROPDOWN_BB,[self.study_deck_ddi,self.check_media_ddi,self.preferences_ddi])
        self.help_dropdown = Dropdown(self.HELP_DROPDOWN_BB,[self.guide_ddi,self.support_ddi,self.about_ddi])
        self.dropdowns: List[Dropdown] = [self.file_dropdown, self.edit_dropdown, self.tools_dropdown, self.help_dropdown]
        
        self.opened_dd: Dropdown = None
        self.add_widgets(self.dropdowns)

        self.study_button: Button = Button(self.STUDY_BB, {self.study_page.open(), self.register_selected_reward(["study_button"])} )
        self.add_card_button: Button = Button(self.ADD_CARD_BB, {self.add_card_page.open(), self.register_selected_reward(["add_card_button"])})
        self.sync_button:  Button = Button(self.SYNC_BB,{self.anki_login.open(), self.register_selected_reward(["anki_login"])})
        self.get_shared_button: Button = Button(self.GET_SHARED_BB, {self.register_selected_reward(["get_shared"])})
        self.create_deck_button: Button = Button(self.CREATE_DECK_BB, {self.add_deck_popup_page.open(), self.register_selected_reward(["create_deck_button"])})
        self.import_file_button: Button = Button(self.IMPORT_FILE_BB, {self.import_page.open(), self.register_selected_reward(["import_file"])})

        self.add_widgets([self.study_button,self.add_card_button,self.sync_button,
        self.get_shared_button,self.create_deck_button,self.import_file_button])

        self.dropdowns_to_str = {
            self.file_dropdown: "file_dropdown",
            self.edit_dropdown: "edit_dropdown",
            self.tools_dropdown: "tools_dropdown",
            self.help_dropdown: "help"
        }

    @property
    def reward_template(self):
        return {
            "add_card_button": 0,
            "anki_login": 0,
            "study_button": 0,
            "decks": [0, 1, 2, 3, 4],
            "get_shared": 0,
            "create_deck_button": 0,
            "import_file": 0,
            "file_dropdown": {
                "opened": 0,
                "selected": [ddi.display_name for ddi in self.file_dropdown.get_all_items()]
            },
            "edit_dropdown": {
                "opened": 0
            },
            "tools_dropdown":{
                "opened": 0,
                "selected": [ddi.display_name for ddi in self.tools_dropdown.get_all_items()]
            },
            "help":{
                "opened": 0,
                "selected": [ddi.display_name for ddi in self.help_dropdown.get_all_items()]
            }
        }
    def get_dropdown_index(self):
        for i,dropdown in self.dropdowns:
            if dropdown.get_current_value() == self.opened_dd:
                return i


    def handle_click(self, click_position: np.ndarray):
        if self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)
            current_value = self.opened_dd.get_current_value()
            self.register_selected_reward([self.dropdowns_to_str[self.opened_dd], "selected", current_value])
            self.opened_dd = None
        
        for dropdown in self.dropdowns:
            if dropdown.is_clicked_by(click_position):
                self.get_state()[5 + self.get_dropdown_index()] = 0
                dropdown.handle_click(click_position)
                if dropdown.is_open():
                    self.opened_dd = dropdown
                    self.get_state()[5 + self.get_dropdown_index()] = 1
                    self.register_selected_reward([self.dropdowns_to_str[dropdown], "opened"])

            return
        
        if (self.profile_page.is_open()):
            self.profile_page.handle_click(click_position)
        elif (self.import_page.is_open()):
            self.import_page.handle_click(click_position)
        elif (self.export_page.is_open()):
            self.export_page.handle_click(click_position)
        elif (self.choose_deck_study_page.is_open()):
            self.choose_deck_study_page.handle_click(click_position)
        elif (self.check_media_page.is_open()):
            self.check_media_page.handle_click(click_position)
        elif (self.preferences_page.is_open()):
            self.preferences_page.handle_click(click_position)
        elif (self.study_page.is_open()):
            self.study_page.handle_click(click_position)
        elif (self.about_page.is_open()):
            self.about_page.handle_click(click_position)
        elif (self.add_card_page.is_open()):
            self.add_card_page.handle_click(click_position)
        elif (self.anki_login.is_open()):
            self.anki_login.handle_click(click_position)
        elif (self.add_deck_popup_page.is_open()):    
            self.add_deck_popup_page.handle_click(click_position)
        elif (self.DECKS_BB.is_point_inside(click_position)):
            self.change_current_deck_index(click_position)
        for widget in self.widgets:
            if (widget.is_clicked_by(click_position)):
                widget.handle_click(click_position)
                return
        
    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (458,30)
        # Top left corner (141,275)
        current_bounding_box = self.calculate_current_bounding_box()
        if((current_bounding_box.is_point_inside(click_point))):
            click_index: int = click_point[1] / 30
            self.get_state()[DeckDatabase().current_index] = 0
            DeckDatabase().current_deck = DeckDatabase().decks[click_index]
            self.get_state()[click_index] = 1
            self.register_selected_reward(["decks", click_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (141,275)
       length = 30 * DeckDatabase().decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 458, length)
       return current_bounding_box

    def open(self):
        self.get_state()[0] = 1
    
    def close(self):
        self.get_state()[0] = 0
    
    def is_open(self):
        return self.get_state()[0]

    def render(self,img: np.ndarray):
        img = super().render(img)
        put_text(img, DeckDatabase().current_deck.name, (326,122), font_scale = 0.3)
        for i, deck in enumerate(DeckDatabase().decks):
            put_text(img, deck.name, (142,424 - i * 30),font_scale=0.3)
        if (self.profile_page.is_open()):
            self.profile_page.render(img)
        elif (self.import_page.is_open()):
            self.import_page.render(img)
        elif (self.export_page.is_open()):
            self.export_page.render(img)
        elif (self.choose_deck_study_page.is_open()):
            self.choose_deck_study_page.render(img)
        elif (self.check_media_page.is_open()):
            self.check_media_page.render(img)
        elif (self.preferences_page.is_open()):
            self.preferences_page.render(img)
        elif (self.study_page.is_open()):
            self.study_page.render(img)
        elif (self.about_page.is_open()):
            self.about_page.render(img)
        elif (self.add_card_page.is_open()):
            self.add_card_page.render(img)
        elif (self.anki_login.is_open()):
            self.anki_login.render(img)
        elif (self.add_deck_popup_page.is_open()):    
            self.add_deck_popup_page.render(img)
        
        return img

    def reset(self):
        ResetCollectionPopupPage().reset_all()
