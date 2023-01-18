from math import floor
import os
from typing import List
import cv2
import numpy as np

from naturalnets.environments.anki import AddCardPage
from naturalnets.environments.anki import AnkiLoginPage
from naturalnets.environments.anki.pages.main_page_popups import AddDeckPopupPage
from naturalnets.environments.anki import EditCardPage
from naturalnets.environments.anki import ResetCollectionPopupPage
from naturalnets.environments.anki.pages.main_page_popups.at_least_one_deck_popup_page import AtLeastOneDeckPopupPage
from naturalnets.environments.anki.pages.main_page_popups.delete_current_deck_check_popup_page import DeleteCurrentDeckPopupPage
from naturalnets.environments.anki.pages.main_page_popups.leads_to_external_website_popup_page import LeadsToExternalWebsitePopupPage
from naturalnets.environments.anki.pages.main_page_popups.no_card_popup_page import NoCardPopupPage
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem
from naturalnets.environments.anki import ChooseDeckStudyPage
from naturalnets.environments.anki import CheckMediaPage
from naturalnets.environments.anki import PreferencesPage
from naturalnets.environments.anki import ImportDeckPage
from naturalnets.environments.anki import ProfilePage
from naturalnets.environments.anki import ExportDeckPage
from naturalnets.environments.anki import DeckDatabase
from naturalnets.environments.anki import AboutPage
from PIL import Image, ImageDraw,ImageFont
from naturalnets.environments.gui_app.enums import Color

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

    WINDOW_BB = BoundingBox(0, 0, 834, 709)
    DECKS_BB = BoundingBox(119, 277, 389, 150)
    
    GET_SHARED_BB = BoundingBox(223, 635, 77, 28)
    CREATE_DECK_BB = BoundingBox(305, 635, 85, 28)
    IMPORT_FILE_BB = BoundingBox(393, 635, 77, 28)
    STUDY_BB = BoundingBox(429, 164, 79, 30)
    DELETE_DECK_BB = BoundingBox(433, 232, 68, 24)

    ADD_CARD_BB = BoundingBox(229, 31, 78, 29)
    DECKS_BUTTON_BB = BoundingBox(393, 32, 69, 27)
    SYNC_BB = BoundingBox(447, 30, 54, 29)
    
    FILE_DROPDOWN_BB = BoundingBox(0, 0, 43, 23)
    EDIT_DROPDOWN_BB = BoundingBox(43, 0, 47, 23)
    TOOLS_DROPDOWN_BB = BoundingBox(90, 0, 53, 23)
    HELP_DROPDOWN_BB = BoundingBox(143, 0, 52, 23)
    
    EDIT_BB = BoundingBox(79, 647, 84, 28)
    SHOW_ANSWER_NEXT_BB = BoundingBox(300, 647, 96, 29)
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
        self.deck_database = DeckDatabase()
        self.leads_to_external_website_popup_page = LeadsToExternalWebsitePopupPage()
        self.delete_current_deck_check_popup_page = DeleteCurrentDeckPopupPage()
        self.at_least_one_deck_popup_page = AtLeastOneDeckPopupPage()
        self.reset_collection_popup_page = ResetCollectionPopupPage()
        self.no_card_popup_page = NoCardPopupPage()

        self.pages: List[Page] = [self.profile_page, self.import_deck_page, self.export_deck_page, self.choose_deck_study_page,
            self.check_media_page, self.preferences_page, self.about_page, self.add_card_page, self.anki_login, self.add_deck_popup_page,
            self.edit_card_page, self.leads_to_external_website_popup_page, self.at_least_one_deck_popup_page, self.reset_collection_popup_page,
            self.no_card_popup_page]
        
        self.add_children([self.profile_page, self.import_deck_page, self.export_deck_page, 
        self.choose_deck_study_page, self.check_media_page, self.preferences_page, self.about_page,
        self.add_card_page, self.add_deck_popup_page, self.edit_card_page, self.anki_login, self.leads_to_external_website_popup_page,
        self.delete_current_deck_check_popup_page, self.at_least_one_deck_popup_page, self.reset_collection_popup_page,self.no_card_popup_page])

        self.switch_profile_ddi = DropdownItem(self.profile_page.open, "Switch Profile")
        self.import_ddi = DropdownItem(self.import_deck_page.open, "Import")
        self.export_ddi = DropdownItem(self.export_deck_page.open, "Export")
        self.exit_ddi = DropdownItem(self.reset_collection_popup_page.reset_all, "Exit")

        self.study_deck_ddi = DropdownItem(self.choose_deck_study_page.open, "Study Deck")
        self.check_media_ddi = DropdownItem(self.check_media_page.open, "Check Media")
        self.preferences_ddi = DropdownItem(self.preferences_page.open, "Preferences")

        self.guide_ddi = DropdownItem(None, "Guide")
        self.support_ddi = DropdownItem(None, "Support")
        self.about_ddi = DropdownItem(self.about_page.open, "About Page")

        self.file_dropdown = Dropdown(self.FILE_DROPDOWN_BB, [self.switch_profile_ddi, self.import_ddi, self.export_ddi, self.exit_ddi])
        self.edit_dropdown = Dropdown(self.EDIT_DROPDOWN_BB, [])
        self.tools_dropdown = Dropdown(self.TOOLS_DROPDOWN_BB, [self.study_deck_ddi, self.check_media_ddi, self.preferences_ddi])
        self.help_dropdown = Dropdown(self.HELP_DROPDOWN_BB, [self.guide_ddi, self.support_ddi, self.about_ddi])
        self.dropdowns: List[Dropdown] = [self.file_dropdown, self.edit_dropdown, self.tools_dropdown, self.help_dropdown]
        
        self.opened_dd: Dropdown = None
        self.add_widget(self.file_dropdown)
        self.add_widget(self.edit_dropdown)
        self.add_widget(self.tools_dropdown)
        self.add_widget(self.help_dropdown)

        self.decks_button = Button(self.DECKS_BUTTON_BB, self.stop_study)
        self.edit_button = Button(self.EDIT_BB, self.edit_card_page.open)
        self.study_button: Button = Button(self.STUDY_BB, self.study)
        self.add_card_button: Button = Button(self.ADD_CARD_BB, self.add_card)
        self.sync_button:  Button = Button(self.SYNC_BB, self.login)
        self.get_shared_button: Button = Button(self.GET_SHARED_BB, self.get_shared)
        self.create_deck_button: Button = Button(self.CREATE_DECK_BB, self.create_deck)
        self.import_file_button: Button = Button(self.IMPORT_FILE_BB, self.import_file)
        self.show_answer_button = Button(self.SHOW_ANSWER_NEXT_BB, self.show_answer)
        self.remove_button = Button(self.REMOVE_BB, self.remove_card)
        self.next_button = Button(self.SHOW_ANSWER_NEXT_BB, self.next_card)
        self.delete_button = Button(self.DELETE_DECK_BB, self.remove_deck)

        self.main_page_widgets = [self.add_card_button, self.sync_button, self.study_button, self.get_shared_button,
        self.create_deck_button ,self.import_file_button, self.delete_button]

        self.study_page_widgets = [self.add_card_button, self.decks_button, self.sync_button, self.edit_button,
        self.show_answer_button, self.remove_button, self.next_button]

        self.dropdowns_to_str = {
            self.file_dropdown: "file_dropdown",
            self.edit_dropdown: "edit_dropdown",
            self.tools_dropdown: "tools_dropdown",
            self.help_dropdown: "help"
        }

        self.set_reward_children([self.anki_login, self.add_deck_popup_page, self.leads_to_external_website_popup_page,
        self.add_card_page, self.import_deck_page, self.delete_current_deck_check_popup_page, self.at_least_one_deck_popup_page,
        self.reset_collection_popup_page,self.edit_card_page,self.no_card_popup_page])

    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "next_card": 0,
            "show_answer": 0,
            "decks": [0, 1, 2, 3, 4],
            "file_dropdown": {
                "opened": 0,
                "selected": ["Switch Profile","Import","Export","Exit"]
            },
            "edit_dropdown": {
                "opened": 0
            },
            "tools_dropdown":{
                "opened": 0,
                "selected": ["Study Deck", "Check Media", "Preferences"]
            },
            "help":{
                "opened": 0,
                "selected": ["Guide", "Support", "About Page"]
            }
        }

    def get_dropdown_index(self):
        for i, dropdown in enumerate(self.dropdowns):
            if dropdown.get_current_value() == self.opened_dd:
                return i


    def handle_click(self, click_position: np.ndarray):       
        if (self.profile_page.is_open()):
            self.profile_page.handle_click(click_position)
            return
        elif (self.import_deck_page.is_open()):
            self.import_deck_page.handle_click(click_position)
            return
        elif (self.export_deck_page.is_open()):
            self.export_deck_page.handle_click(click_position)
            return
        elif (self.choose_deck_study_page.is_open()):
            self.choose_deck_study_page.handle_click(click_position)
            return
        elif (self.check_media_page.is_open()):
            self.check_media_page.handle_click(click_position)
            return
        elif (self.preferences_page.is_open()):
            self.preferences_page.handle_click(click_position)
            return
        elif (self.edit_card_page.is_open()):
            self.edit_card_page.handle_click(click_position)
            return
        elif (self.about_page.is_open()):
            self.about_page.handle_click(click_position)
            return
        elif (self.add_card_page.is_open()):
            self.add_card_page.handle_click(click_position)
            return
        elif (self.anki_login.is_open()):
            self.anki_login.handle_click(click_position)
            return
        elif (self.add_deck_popup_page.is_open()):    
            self.add_deck_popup_page.handle_click(click_position)
            return
        elif (self.leads_to_external_website_popup_page.is_open()):
            self.leads_to_external_website_popup_page.handle_click(click_position)
            return
        elif (self.delete_current_deck_check_popup_page.is_open()):
            self.delete_current_deck_check_popup_page.handle_click(click_position)
            return
        elif (self.at_least_one_deck_popup_page.is_open()):
            self.at_least_one_deck_popup_page.handle_click(click_position)
            return
        elif (self.no_card_popup_page.is_open()):
            self.no_card_popup_page.handle_click(click_position)
            return
        elif (self.DECKS_BB.is_point_inside(click_position) and self.get_state()[6] == 0):
            self.change_current_deck_index(click_position)
            return
        elif self.opened_dd is not None:
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
                   
        if (self.get_state()[6] == 0):
            print(self.get_state()[7])
            for widget in self.main_page_widgets:
                if widget.is_clicked_by(click_position):
                    widget.handle_click(click_position)
                    return
        
        elif (self.get_state()[7] == 0):
            for widget in self.study_page_widgets:
                if widget is self.next_button:
                    pass
                elif (widget.is_clicked_by(click_position)):
                    widget.handle_click(click_position)
                    return
        
        elif (self.get_state()[7] == 1):
            for widget in self.study_page_widgets:
                if widget is self.show_answer_button:
                    pass
                elif (widget.is_clicked_by(click_position)):
                    widget.handle_click(click_position)
                    return

    def add_card(self):
        self.add_card_page.open()

    def login(self):
        self.anki_login.open() 

    def create_deck(self):
        self.add_deck_popup_page.open() 

    def import_file(self):
        self.import_deck_page.open()

    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (458,30)
        # Top left corner (141,275)
        current_bounding_box = self.calculate_current_bounding_box()
        if((current_bounding_box.is_point_inside(click_point))):
            click_index: int = floor((click_point[1] - 275) / 30)
            self.get_state()[self.deck_database.current_index] = 0
            self.deck_database.current_deck = self.deck_database.decks[click_index]
            self.deck_database.current_index = click_index
            self.deck_database.set_current_index(click_index)
            self.get_state()[click_index] = 1
            self.register_selected_reward(["decks", click_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (106,275)
       length = 30 * self.deck_database.decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 458, length)
       return current_bounding_box

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])
    
    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])
    
    def is_open(self):
        return self.get_state()[0]
    
    def study(self):
        if(len(self.deck_database.current_deck.cards) == 0):
            self.no_card_popup_page.open()
        else:
            self.get_state()[6] = 1
    
    def stop_study(self):
        self.get_state()[6] = 0

    def next_card(self):
        self.get_state()[7] = 0
        self.register_selected_reward(["next_card"])
        self.deck_database.current_deck.increment_study_index()

    def show_answer(self):
        self.get_state()[7] = 1
        self.register_selected_reward(["show_answer"])
    
    def render(self,img: np.ndarray):
        if(self.get_state()[6] == 1):
            img = self.render_study_page(img)
        elif(self.get_state()[6] == 0):
            img = self.render_deck_page(img)
        img = self.render_onto_current(img)
        return img

    def render_onto_current(self,img: np.ndarray):
        if (self.profile_page.is_open()):
            img = self.profile_page.render(img)
        elif (self.import_deck_page.is_open()):
            img = self.import_deck_page.render(img)
        elif (self.export_deck_page.is_open()):
            img = self.export_deck_page.render(img)
        elif (self.choose_deck_study_page.is_open()):
            img = self.choose_deck_study_page.render(img)
        elif (self.check_media_page.is_open()):
            img = self.check_media_page.render(img)
        elif (self.preferences_page.is_open()):
            img = self.preferences_page.render(img)
        elif (self.about_page.is_open()):
            img = self.about_page.render(img)
        elif (self.add_card_page.is_open()):
            img = self.add_card_page.render(img)
        elif (self.anki_login.is_open()):
            img = self.anki_login.render(img)
        elif (self.add_deck_popup_page.is_open()):    
            img = self.add_deck_popup_page.render(img)
        elif (self.leads_to_external_website_popup_page.is_open()):
            img = self.leads_to_external_website_popup_page.render(img)
        elif (self.delete_current_deck_check_popup_page.is_open()):
            img = self.delete_current_deck_check_popup_page.render(img)
        elif (self.at_least_one_deck_popup_page.is_open()):
            img = self.at_least_one_deck_popup_page.render(img)
        elif (self.no_card_popup_page.is_open()):
            img = self.no_card_popup_page.render(img)
        return img

    def render_deck_page(self,img: np.ndarray):
        frame = cv2.imread(self.IMG_PATH)
        render_onto_bb(img, self.WINDOW_BB, frame)
        if (self.profile_page.current_profile is not None):
            put_text(img, f"Current profile: {self.profile_page.current_profile.name}", (16,122), font_scale = 0.5)
        
        put_text(img, f"Current deck: {self.deck_database.current_deck.name}", (226,122), font_scale = 0.5)
        
        if (self.anki_login.current_anki_account is not None):
            put_text(img, f"Current account: {self.anki_login.current_anki_account.account_name}", (556,122), font_scale = 0.5)
        
        for i, deck in enumerate(self.deck_database.decks):
            put_text(img, deck.name, (148,296 + i * 30), font_scale = 0.5)
        return img

    def render_study_page(self,img: np.ndarray):
        frame = cv2.imread(self.IMG_PATH_STUDY)
        render_onto_bb(img, self.WINDOW_BB, frame)
        self.print_question_answer(img, f"Question : {self.deck_database.current_deck.cards[self.deck_database.current_deck.study_index].front}", BoundingBox (116, 76, 600, 100))
        if (self.get_state()[7] == 1):
            self.print_question_answer(img, f"Answer : {self.deck_database.current_deck.cards[self.deck_database.current_deck.study_index].back}", BoundingBox (116, 166, 600, 100))
            button = cv2.imread(self.NEXT_BUTTON_PATH)
            render_onto_bb(img, BoundingBox (352, 646, 115, 29), button)
        if (self.edit_card_page.is_open()):
            img = self.edit_card_page.render(img)
        return img
    
    def get_shared(self):
        self.leads_to_external_website_popup_page.open()

    def remove_card(self):
        self.deck_database.current_deck.cards.remove(self.deck_database.current_deck[self.deck_database.current_deck.study_index])
    
    def remove_deck(self):
        if(self.deck_database.decks_length() == 1):
            self.at_least_one_deck_popup_page.open()
            return
        self.delete_current_deck_check_popup_page.open()

    def print_question_answer(self, img: np.ndarray, text: str, bounding_box: BoundingBox):
        
        image = np.zeros((100, 600, 3), dtype=np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
        pil_image = Image.fromarray(image)
        
        draw = ImageDraw.Draw(pil_image)
        font = ImageFont.truetype("arial.ttf", 35)
        draw.text((110, 30), text, font=font)
        pil_image = np.invert(pil_image)
        image = np.asarray(pil_image)

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        render_onto_bb(img, bounding_box, image)
        
        return img