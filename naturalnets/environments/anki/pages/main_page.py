import os
from typing import List
import cv2
import numpy as np

from pages import AddCardPage
from pages import AnkiLoginPage
from main_page_popups import AddDeckPopupPage
from pages import EditCardPage
from pages import ResetCollectionPopupPage
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem
from pages import ChooseDeckStudyPage
from pages import CheckMediaPage
from pages import PreferencesPage
from pages import ImportDeckPage
from pages import ProfilePage
from pages import ExportDeckPage
from anki import DeckDatabase
from pages import AboutPage

class MainPage(Page,RewardElement):
    
    """
    State description:
            state[0]: if this window is open
            state[i]: i-th deck is selected i = {1, 2, 3, 4, 5}
            state[6]: learning window is active
            state[7]: answer is shown
    """

    STATE_LEN = 8
    IMG_PATH = os.path.join(IMAGES_PATH, "main_page.png")
    IMG_PATH_STUDY = os.path.join(IMAGES_PATH, "study_page.png")
    NEXT_BUTTON_PATH = os.path.join(IMAGES_PATH, "next_button.png")

    WINDOW_BB = BoundingBox(0, 0, 834, 710)
    DECKS_BB = BoundingBox(141, 276, 458, 150)
    
    GET_SHARED_BB = BoundingBox(262, 635, 93, 28)
    CREATE_DECK_BB = BoundingBox(360, 635, 100, 28)
    IMPORT_FILE_BB = BoundingBox(463, 635, 91, 28)
    STUDY_BB = BoundingBox(505, 165, 92, 27)

    ADD_CARD_BB = BoundingBox(269, 31, 82, 29)
    DECKS_BUTTON_BB = BoundingBox(393, 32, 69, 27)
    SYNC_BB = BoundingBox(525, 30, 54, 29)
    
    FILE_DROPDOWN_BB = BoundingBox(0, 0, 43, 23)
    EDIT_DROPDOWN_BB = BoundingBox(43, 0, 47, 23)
    TOOLS_DROPDOWN_BB = BoundingBox(90, 0, 53, 23)
    HELP_DROPDOWN_BB = BoundingBox(143, 0, 52, 23)
    
    EDIT_BB = BoundingBox(10, 698, 100, 28)
    SHOW_ANSWER_NEXT_BB = BoundingBox(379, 696, 115, 31)
    REMOVE_BB = BoundingBox(764, 698, 100, 28)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MainPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.profile_page = ProfilePage()
        self.import_deck_page = ImportDeckPage()
        self.export_deck_page = ExportDeckPage()
        self.choose_deck_study_page = ChooseDeckStudyPage()
        self.check_media_page = CheckMediaPage()
        self.preferences_page = PreferencesPage()
        self.about_page = AboutPage()
        self.add_card_page = AddCardPage()
        self.anki_login = AnkiLoginPage()
        self.add_deck_popup_page = AddDeckPopupPage()
        self.edit_card_page = EditCardPage()

        self.pages: List[Page] = [self.profile_page, self.import_deck_page, self.export_deck_page, self.choose_deck_study_page,
            self.check_media_page, self.preferences_page, self.about_page, self.add_card_page, self.anki_login, self.add_deck_popup_page,
            self.edit_card_page]
        
        self.add_children([self.profile_page, self.import_deck_page, self.export_deck_page, 
        self.choose_deck_study_page, self.check_media_page, self.preferences_page, self.about_page, 
        self.add_card_page, self.add_deck_popup_page, self.edit_card_page, self.anki_login])

        self.switch_profile_ddi = DropdownItem(self.profile_page.open, "Switch Profile")
        self.import_ddi = DropdownItem(self.import_deck_page.open, "Import")
        self.export_ddi = DropdownItem(self.export_deck_page.open, "Export")
        self.exit_ddi = DropdownItem(ResetCollectionPopupPage().reset_all, "Exit")

        self.study_deck_ddi = DropdownItem(self.choose_deck_study_page.open, "Study Deck")
        self.check_media_ddi = DropdownItem(self.check_media_page.open, "Check Media")
        self.preferences_ddi = DropdownItem(self.preferences_page.open, "Preferences")

        self.guide_ddi = DropdownItem(None, "Guide")
        self.support_ddi = DropdownItem(None, "Support")
        self.about_ddi = DropdownItem(self.about_page.open(), "About Page")

        self.file_dropdown = Dropdown(self.FILE_DROPDOWN_BB, [self.switch_profile_ddi, self.import_ddi, self.export_ddi, self.exit_ddi])
        self.edit_dropdown = Dropdown(self.EDIT_DROPDOWN_BB, [])
        self.tools_dropdown = Dropdown(self.TOOLS_DROPDOWN_BB, [self.study_deck_ddi, self.check_media_ddi, self.preferences_ddi])
        self.help_dropdown = Dropdown(self.HELP_DROPDOWN_BB, [self.guide_ddi, self.support_ddi, self.about_ddi])
        self.dropdowns: List[Dropdown] = [self.file_dropdown, self.edit_dropdown, self.tools_dropdown, self.help_dropdown]
        
        self.opened_dd: Dropdown = None
        self.add_children(self.dropdowns)
        self.add_widgets(self.dropdowns)

        self.decks_button = Button(self.DECKS_BUTTON_BB, self.stop_study)
        self.edit_button = Button(self.EDIT_BB, self.edit_card_page.open)
        self.study_button: Button = Button(self.STUDY_BB, self.study)
        self.add_card_button: Button = Button(self.ADD_CARD_BB, self.add_card)
        self.sync_button:  Button = Button(self.SYNC_BB, self.login)
        self.get_shared_button: Button = Button(self.GET_SHARED_BB, self.register_selected_reward(["get_shared"]))
        self.create_deck_button: Button = Button(self.CREATE_DECK_BB, self.create_deck)
        self.import_file_button: Button = Button(self.IMPORT_FILE_BB, self.import_file)
        self.show_answer_button = Button(self.SHOW_ANSWER_NEXT_BB, self.show_answer)
        self.remove_button = Button(self.REMOVE_BB, DeckDatabase().current_deck.cards.remove(DeckDatabase().current_deck[DeckDatabase().current_deck.study_index]))
        self.next_button = Button(self.SHOW_ANSWER_NEXT_BB, self.next_card)

        self.add_widgets([self.study_button, self.add_card_button, self.sync_button,
        self.get_shared_button, self.create_deck_button, self.import_file_button, self.edit_button,
        self.show_answer_button, self.remove_button, self.next_button])

        self.main_page_widgets = self.dropdowns + [self.add_card_button,self.sync_button,self.study_button,self.get_shared_button,
        self.create_deck_button,self.import_file_button]

        self.study_page_widgets = self.dropdowns + [self.add_card_button, self.decks_button, self.sync_button, self.edit_button,
        self.show_answer_button, self.remove_button, self.next_button]

        self.dropdowns_to_str = {
            self.file_dropdown: "file_dropdown",
            self.edit_dropdown: "edit_dropdown",
            self.tools_dropdown: "tools_dropdown",
            self.help_dropdown: "help"
        }

    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "next_card": 0,
            "show_answer": 0,
            "add_card_button": 0,
            "anki_login": 0,
            "study": [True, False],
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
        for i, dropdown in enumerate(self.dropdowns):
            if dropdown.get_current_value() == self.opened_dd:
                return i


    def handle_click(self, click_position: np.ndarray):
        if self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)
            current_value = self.opened_dd.get_current_value()
            if(current_value is not None):
                self.register_selected_reward([self.dropdowns_to_str[self.opened_dd], "selected", current_value])
            self.opened_dd = None
        
        for dropdown in self.dropdowns:
            if dropdown.is_clicked_by(click_position):
                dropdown.handle_click(click_position)
                if dropdown.is_open():
                    self.opened_dd = dropdown
                    self.register_selected_reward([self.dropdowns_to_str[dropdown], "opened"])
            return
        
        if (self.profile_page.is_open()):
            self.profile_page.handle_click(click_position)
        elif (self.import_deck_page.is_open()):
            self.import_deck_page.handle_click(click_position)
        elif (self.export_deck_page.is_open()):
            self.export_deck_page.handle_click(click_position)
        elif (self.choose_deck_study_page.is_open()):
            self.choose_deck_study_page.handle_click(click_position)
        elif (self.check_media_page.is_open()):
            self.check_media_page.handle_click(click_position)
        elif (self.preferences_page.is_open()):
            self.preferences_page.handle_click(click_position)
        elif (self.edit_card_page.is_open()):
            self.edit_card_page.handle_click(click_position)
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

        if (self.get_state()[6] == 0):
            for widget in self.main_page_widgets:
                if widget.is_clicked_by(click_position):
                    self.handle_click(click_position)
        elif (self.get_state()[7] == 0):
            for widget in self.study_page_widgets:
                if widget is self.next_button:
                    pass
                elif (widget.is_clicked_by(click_position)):
                    widget.handle_click(click_position)
        elif (self.get_state()[7] == 1):
            for widget in self.study_page_widgets:
                if widget is self.show_answer_button:
                    pass
                elif (widget.is_clicked_by(click_position)):
                    widget.handle_click(click_position)
        
    def add_card(self):
        self.add_card_page.open()
        self.register_selected_reward(["add_card_button"])

    def login(self):
        self.anki_login.open() 
        self.register_selected_reward(["anki_login"])

    def create_deck(self):
        self.add_deck_popup_page.open() 
        self.register_selected_reward(["create_deck_button"])

    def import_file(self):
        self.import_deck_page.open()
        self.register_selected_reward(["import_file"])

    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (458,30)
        # Top left corner (141,275)
        current_bounding_box = self.calculate_current_bounding_box()
        if((current_bounding_box.is_point_inside(click_point))):
            click_index: int = (click_point[1] - 275) / 30
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
        self.register_selected_reward(["window","open"])
    
    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def is_open(self):
        return self.get_state()[0]

    def render(self,img: np.ndarray):
        img = self.render_onto_current(img)
        return img
    
    def study(self):
        self.register_selected_reward(["study", True])
        self.get_state()[6] = 1
    
    def stop_study(self):
        self.get_state()[6] = 0
        if(self.get_state()[6] == 1):
            self.register_selected_reward(["study", False])

    def next_card(self):
        self.get_state()[7] = 0
        self.register_selected_reward(["next_card"])
        DeckDatabase().current_deck.increment_study_index()

    def show_answer(self):
        self.get_state()[7] = 1
        self.register_selected_reward(["show_answer"])
    
    def render(self,img: np.ndarray):
        if(self.get_state()[6] == 1):
            self.render_study_page(img)
        elif(self.get_state()[6] == 0):
            self.render_deck_page(img)
        img = self.render_onto_current(img)
        return img

    def render_onto_current(self,img: np.ndarray):
        if (self.profile_page.is_open()):
            self.profile_page.render(img)
        elif (self.import_deck_page.is_open()):
            self.import_deck_page.render(img)
        elif (self.export_deck_page.is_open()):
            self.export_deck_page.render(img)
        elif (self.choose_deck_study_page.is_open()):
            self.choose_deck_study_page.render(img)
        elif (self.check_media_page.is_open()):
            self.check_media_page.render(img)
        elif (self.preferences_page.is_open()):
            self.preferences_page.render(img)
        elif (self.about_page.is_open()):
            self.about_page.render(img)
        elif (self.add_card_page.is_open()):
            self.add_card_page.render(img)
        elif (self.anki_login.is_open()):
            self.anki_login.render(img)
        elif (self.add_deck_popup_page.is_open()):    
            self.add_deck_popup_page.render(img)
        return img

    def render_deck_page(self,img: np.ndarray):
        frame = cv2.imread(self.IMG_PATH)
        render_onto_bb(img, self.WINDOW_BB, frame)
        put_text(img, DeckDatabase().current_deck.name, (326,122), font_scale = 0.3)
        for i, deck in enumerate(DeckDatabase().decks):
            put_text(img, deck.name, (148,298 + i * 30), font_scale=0.3)

    def render_study_page(self,img: np.ndarray):
        frame = cv2.imread(self.IMG_PATH_STUDY)
        render_onto_bb(img, self.WINDOW_BB, frame)
        put_text(img, DeckDatabase().current_deck.cards[DeckDatabase().current_deck.study_index].front, (340 ,120), font_scale = 0.3)
        if (self.get_state()[7] == 1):
            put_text(img, DeckDatabase().current_deck.cards[DeckDatabase().current_deck.study_index].back, (340 ,160), font_scale = 0.3)
            button = cv2.imread(self.NEXT_BUTTON_PATH)
            render_onto_bb(img, self.SHOW_ANSWER_NEXT_BB, button)
        if (self.edit_card_page.open()):
            self.edit_card_page.render(img)
    
    def close_all_children(self):
        for child in self.get_children():
            child.get_state()[0] = 0