from math import floor
import os
from typing import List
import cv2
import numpy as np

from naturalnets.environments.anki import AddCardPage
from naturalnets.environments.anki import AnkiLoginPage
from naturalnets.environments.anki.pages.main_page_popups import AddDeckPopup
from naturalnets.environments.anki import EditCardPage
from naturalnets.environments.anki import ResetCollectionPopup
from naturalnets.environments.anki.pages.main_page_popups.at_least_one_card_popup import AtLeastOneCardPopup
from naturalnets.environments.anki.pages.main_page_popups.at_least_one_deck_popup import AtLeastOneDeckPopup
from naturalnets.environments.anki.pages.main_page_popups.delete_current_deck_check_popup import DeleteCurrentDeckPopup
from naturalnets.environments.anki.pages.main_page_popups.leads_to_external_website_popup import LeadsToExternalWebsitePopup
from naturalnets.environments.anki.pages.main_page_popups.no_card_popup import NoCardPopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb, print_non_ascii
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem
from naturalnets.environments.anki import ChooseDeckStudyPage
from naturalnets.environments.anki import CheckMediaPage
from naturalnets.environments.anki import PreferencesPage
from naturalnets.environments.anki import ImportDeckPage
from naturalnets.environments.anki import ProfilePage
from naturalnets.environments.anki import ExportDeckPage
from naturalnets.environments.anki import AboutPage

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
    DECKS_BUTTON_PATH = os.path.join(IMAGES_PATH, "decks_button.png")

    WINDOW_BB = BoundingBox(0, 0, 834, 834)
    DECKS_BB = BoundingBox(112, 244, 610, 196)
    
    DECKS_BUTTON_BB = BoundingBox(481, 44, 155, 36)
    CREATE_DECK_BB = BoundingBox(15, 727, 254, 48)
    IMPORT_FILE_BB = BoundingBox(586, 726, 235, 48)
    DELETE_DECK_BB = BoundingBox(303, 724, 252, 48)

    STUDY_BB = BoundingBox(281, 458, 260, 50)
    ADD_CARD_BB = BoundingBox(298, 44, 155, 36)
    GET_SHARED_BB = BoundingBox(481, 45, 155, 36)
    ANKI_LOGIN_BB = BoundingBox(656, 44, 155, 36)

    FILE_DROPDOWN_BB = BoundingBox(0, 0, 70, 29)
    EDIT_DROPDOWN_BB = BoundingBox(70, 0, 70, 29)
    TOOLS_DROPDOWN_BB = BoundingBox(140, 0, 70, 29)
    HELP_DROPDOWN_BB = BoundingBox(210, 0, 70, 29)
    
    FILE_DROPDOWN_BB_OFFSET = BoundingBox(0, 33, 100, 28)
    EDIT_DROPDOWN_BB_OFFSET = BoundingBox(70, 33, 90, 28)
    TOOLS_DROPDOWN_BB_OFFSET = BoundingBox(140, 33, 90, 28)
    HELP_DROPDOWN_BB_OFFSET = BoundingBox(210, 33, 90, 28)

    EDIT_BB = BoundingBox(71, 773, 88, 37)
    SHOW_ANSWER_NEXT_BB = BoundingBox(312, 773, 140, 34)
    REMOVE_BB = BoundingBox(624, 773, 129, 35)

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
        self.add_deck_popup_page = AddDeckPopup()
        self.edit_card_page = EditCardPage()
        
        self.profile_database = ProfileDatabase()
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database

        self.leads_to_external_website_popup_page = LeadsToExternalWebsitePopup()
        self.delete_current_deck_check_popup_page = DeleteCurrentDeckPopup()
        self.at_least_one_deck_popup_page = AtLeastOneDeckPopup()
        self.reset_collection_popup_page = ResetCollectionPopup()
        self.no_card_popup_page = NoCardPopup()
        self.at_least_one_card_popup_page = AtLeastOneCardPopup()
        self.choose_deck_study_page = ChooseDeckStudyPage()

        self.pages: List[Page] = [self.profile_page, self.import_deck_page, self.export_deck_page, self.choose_deck_study_page,
            self.check_media_page, self.preferences_page, self.about_page, self.add_card_page, self.anki_login, self.add_deck_popup_page,
            self.edit_card_page, self.leads_to_external_website_popup_page, self.at_least_one_deck_popup_page, self.reset_collection_popup_page,
            self.no_card_popup_page, self.at_least_one_card_popup_page, self.delete_current_deck_check_popup_page]
        
        self.add_children([self.profile_page, self.import_deck_page, self.export_deck_page, 
        self.choose_deck_study_page, self.check_media_page, self.preferences_page, self.about_page,
        self.add_card_page, self.add_deck_popup_page, self.edit_card_page, self.anki_login, self.leads_to_external_website_popup_page,
        self.delete_current_deck_check_popup_page, self.at_least_one_deck_popup_page, self.reset_collection_popup_page,self.no_card_popup_page,
        self.at_least_one_card_popup_page, self.choose_deck_study_page, self.preferences_page])

        self.switch_profile_ddi = DropdownItem("Switch Profile", "Switch Profile")
        self.switch_profile_ddi.set_click_action(self.open_switch_profile)
        self.import_ddi = DropdownItem("Import", "Import")
        self.import_ddi.set_click_action(self.open_import_deck_page)
        self.export_ddi = DropdownItem("Export", "Export")
        self.export_ddi.set_click_action(self.open_export_deck_page)
        self.exit_ddi = DropdownItem("Exit", "Exit")
        self.exit_ddi.set_click_action(self.open_reset_collection_popup)

        self.study_deck_ddi = DropdownItem("Study Deck", "Study Deck")
        self.study_deck_ddi.set_click_action(self.open_choose_deck_study_page)
        self.check_media_ddi = DropdownItem("Check Media", "Check Media")
        self.check_media_ddi.set_click_action(self.check_media_page.open)
        self.preferences_ddi = DropdownItem("Preferences", "Preferences")
        self.preferences_ddi.set_click_action(self.open_preferences_page)
        
        self.show_anki_logo_ddi = DropdownItem("Anki Logo", "Anki Logo")
        self.show_anki_logo_ddi.set_click_action(self.set_logo_shown)

        self.guide_ddi = DropdownItem("Guide", "Guide")
        self.guide_ddi.set_click_action(self.leads_to_external_website_popup_page.open)
        self.support_ddi = DropdownItem("Support", "Support")
        self.support_ddi.set_click_action(self.leads_to_external_website_popup_page.open)
        self.about_ddi = DropdownItem("About Page", "About Page")
        self.about_ddi.set_click_action(self.about_page.open)
  
        self.file_dropdown = Dropdown(self.FILE_DROPDOWN_BB_OFFSET, [self.switch_profile_ddi, self.import_ddi, self.export_ddi, self.exit_ddi])
        self.edit_dropdown = Dropdown(self.EDIT_DROPDOWN_BB_OFFSET, [self.show_anki_logo_ddi])
        self.tools_dropdown = Dropdown(self.TOOLS_DROPDOWN_BB_OFFSET, [self.study_deck_ddi, self.check_media_ddi, self.preferences_ddi])
        self.help_dropdown = Dropdown(self.HELP_DROPDOWN_BB_OFFSET, [self.guide_ddi, self.support_ddi, self.about_ddi])
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
        self.sync_button:  Button = Button(self.ANKI_LOGIN_BB, self.login)
        self.get_shared_button: Button = Button(self.GET_SHARED_BB, self.leads_to_external_website_popup_page.open)
        self.create_deck_button: Button = Button(self.CREATE_DECK_BB, self.create_deck)
        self.import_file_button: Button = Button(self.IMPORT_FILE_BB, self.import_file)
        self.show_answer_button = Button(self.SHOW_ANSWER_NEXT_BB, self.show_answer)
        self.remove_button = Button(self.REMOVE_BB, self.remove_card)
        self.next_button = Button(self.SHOW_ANSWER_NEXT_BB, self.next_card)
        self.delete_button = Button(self.DELETE_DECK_BB, self.remove_deck)
        self.study_button_study_deck: Button = Button(self.choose_deck_study_page.STUDY_BB, self.study_deck)

        self.main_page_widgets = [self.add_card_button, self.sync_button, self.study_button, self.get_shared_button,
        self.create_deck_button ,self.import_file_button, self.delete_button]

        self.study_page_widgets = [self.add_card_button, self.decks_button, self.sync_button, self.edit_button,
        self.show_answer_button, self.remove_button, self.next_button]

        self.dropdown_bbs = [self.FILE_DROPDOWN_BB, self.EDIT_DROPDOWN_BB, self.TOOLS_DROPDOWN_BB ,self.HELP_DROPDOWN_BB]

        self.dropdowns_to_str = {
            self.file_dropdown: "file_dropdown",
            self.edit_dropdown: "edit_dropdown",
            self.tools_dropdown: "tools_dropdown",
            self.help_dropdown: "help"
        }
        
        self.bounding_boxes_to_dropdowns = {
            self.FILE_DROPDOWN_BB: self.file_dropdown,
            self.EDIT_DROPDOWN_BB: self.edit_dropdown,
            self.TOOLS_DROPDOWN_BB: self.tools_dropdown,
            self.HELP_DROPDOWN_BB: self.help_dropdown
        }

        self.set_reward_children([self.profile_page, self.anki_login, self.add_deck_popup_page, self.leads_to_external_website_popup_page,
        self.add_card_page, self.import_deck_page, self.delete_current_deck_check_popup_page, self.at_least_one_deck_popup_page,
        self.reset_collection_popup_page,self.edit_card_page,self.no_card_popup_page,self.at_least_one_card_popup_page,self.about_page,
        self.check_media_page, self.choose_deck_study_page, self.preferences_page,self.profile_page, self.export_deck_page])
        
        self.is_logo_enabled = False

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
                "opened": 0,
                "selected": ["Anki Logo"]
            },
            "tools_dropdown":{
                "opened": 0,
                "selected": ["Study Deck", "Check Media", "Preferences"]
            },
            "help":{
                "opened": 0,
                "selected": ["Guide", "Support", "About Page"]
            },
            "study": 0,
            "remove_card": 0,
            "remove_deck": 0,
            "stop_study": 0,
            "logo_shown": [True, False]
        }

    def get_dropdown_index(self):
        for i, dropdown in enumerate(self.dropdowns):
            if dropdown.get_current_value() == self.opened_dd:
                return i

    def handle_click(self, click_position: np.ndarray):       
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        if (self.profile_page.is_open()):
            self.profile_page.handle_click(click_position)
            return
        elif (self.about_page.is_open()):
            self.about_page.handle_click(click_position)
            return
        elif (self.check_media_page.is_open()):
            self.check_media_page.handle_click(click_position)
            return
        elif (self.import_deck_page.is_open()):
            self.import_deck_page.handle_click(click_position)
            return
        elif (self.export_deck_page.is_open()):
            self.export_deck_page.handle_click(click_position)
            return
        elif (self.preferences_page.is_open()):
            self.preferences_page.handle_click(click_position)
            return
        elif (self.edit_card_page.is_open()):
            self.edit_card_page.handle_click(click_position)
            return
        elif (self.add_card_page.is_open()):
            self.add_card_page.handle_click(click_position)
            return
        elif (self.choose_deck_study_page.is_open()):
            # Cannot be handled in choose deck page itself so it is handled here
            if (self.study_button_study_deck.is_clicked_by(click_position)):
                self.study_button_study_deck.handle_click(click_position)
            else:
                self.choose_deck_study_page.handle_click(click_position)
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
        elif (self.at_least_one_card_popup_page.is_open()):
            self.at_least_one_card_popup_page.handle_click(click_position)
            return
        elif (self.reset_collection_popup_page.is_open()):
            self.reset_collection_popup_page.handle_click(click_position)
            return
        elif self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)
            current_value = self.opened_dd.get_current_value()
            self.opened_dd.close()
            if(current_value is not None):
                self.register_selected_reward([self.dropdowns_to_str[self.opened_dd], "selected", current_value])
            self.opened_dd = None
            return

        elif (self.DECKS_BB.is_point_inside(click_position) and self.get_state()[6] == 0):
            self.change_current_deck_index(click_position)
            return
        
        for bounding_box in self.dropdown_bbs:
            if bounding_box.is_point_inside(click_position):
                self.bounding_boxes_to_dropdowns[bounding_box].handle_click(click_position)
                if self.bounding_boxes_to_dropdowns[bounding_box].is_open():
                    self.opened_dd = self.bounding_boxes_to_dropdowns[bounding_box]
                    self.register_selected_reward([self.dropdowns_to_str[self.bounding_boxes_to_dropdowns[bounding_box]], "opened"])
                   
        if (self.get_state()[6] == 0):
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
        self.get_state()[6] = 0
        self.add_card_page.open()

    def login(self):
        self.get_state()[6] = 0
        self.anki_login.open() 

    def create_deck(self):
        self.add_deck_popup_page.open() 

    def import_file(self):
        self.get_state()[6] = 0
        self.import_deck_page.open()

    def change_current_deck_index(self,click_point:np.ndarray):
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        current_bounding_box = self.calculate_current_bounding_box()
        if((current_bounding_box.is_point_inside(click_point))):
            click_index: int = floor((click_point[1] - 246) / 38)
            if(click_index >= self.deck_database.decks_length()):
                return
            self.get_state()[self.deck_database.current_index + 1] = 0
            self.deck_database.set_current_index(click_index)
            self.get_state()[click_index + 1] = 1
            self.register_selected_reward(["decks", click_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (112,246)
       length = 38 * self.deck_database.decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 610, length)
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
        if(len(self.deck_database.decks[self.deck_database.current_index].cards) == 0):
            self.no_card_popup_page.open()
        else:
            self.register_selected_reward(["study"])
            self.get_state()[6] = 1
            self.get_state()[7] = (1 if self.deck_database.decks[self.deck_database.current_index].is_answer_shown else 0)
    
    def stop_study(self):
        self.register_selected_reward(["stop_study"])
        self.get_state()[6] = 0

    def next_card(self):
        self.get_state()[7] = 0
        self.deck_database.decks[self.deck_database.current_index].is_answer_shown = False
        self.register_selected_reward(["next_card"])
        self.deck_database.decks[self.deck_database.current_index].increment_study_index()

    def show_answer(self):
        self.deck_database.decks[self.deck_database.current_index].is_answer_shown = True
        self.get_state()[7] = 1
        self.register_selected_reward(["show_answer"])
    
    def render(self,img: np.ndarray):
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
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
        elif (self.at_least_one_card_popup_page.is_open()):
            img = self.at_least_one_card_popup_page.render(img)
        elif (self.check_media_page.is_open()):
            img = self.check_media_page.render(img)
        elif (self.reset_collection_popup_page.is_open()):
            img = self.reset_collection_popup_page.render(img)
        elif (self.opened_dd is not None):
            img = self.opened_dd.render(img)
        return img


    def render_deck_page(self,img: np.ndarray):
        frame = cv2.imread(self.IMG_PATH)
        render_onto_bb(img, self.WINDOW_BB, frame)
        anki_logo = cv2.imread(IMAGES_PATH + "anki_logo.png")
        if(self.is_logo_enabled):
            render_onto_bb(img, BoundingBox (657, 450, 128, 128), anki_logo)
        if (self.profile_page.current_profile is not None):
            put_text(img, f"Current profile: {self.profile_database.profiles[self.profile_database.current_index].name}", (16,132), font_scale = 0.4)
        
        put_text(img, f"Current deck: {self.deck_database.decks[self.deck_database.current_index].name}", (286,132), font_scale = 0.4)
        
        if (self.anki_login.current_anki_account is not None):
            put_text(img, f"Current account: {self.anki_login.current_anki_account.account_name}", (556,132), font_scale = 0.4)
        
        for i, deck in enumerate(self.deck_database.decks):
            put_text(img, deck.name, (126 ,271 + i * 38), font_scale = 0.5)
        return img

    def render_study_page(self,image: np.ndarray):
        frame = cv2.imread(self.IMG_PATH_STUDY)
        render_onto_bb(image, self.WINDOW_BB, frame)
        decks_button = cv2.imread(self.DECKS_BUTTON_PATH)
        render_onto_bb(image, BoundingBox (479, 43, 158, 40), decks_button)
        put_text(image, f"Current deck: {self.deck_database.decks[self.deck_database.current_index].name}",(484, 112),font_scale = 0.5)
        put_text(image, f"Current card number: {self.deck_database.decks[self.deck_database.current_index].study_index + 1}",(484, 142),font_scale = 0.5)
        put_text(image, f"Number of cards: {self.deck_database.decks[self.deck_database.current_index].deck_length()}",(484, 172),font_scale = 0.5)
        print_non_ascii(img = image, text = f"Question : {self.deck_database.decks[self.deck_database.current_index].cards[self.deck_database.decks[self.deck_database.current_index].study_index].front}",bounding_box = BoundingBox(42, 232, 600, 100), font_size = 35, dimension = (100, 600, 3))
        if(self.leads_to_external_website_popup_page.is_open()):
            image = self.leads_to_external_website_popup_page.render(image)
        if (self.get_state()[7] == 1):
            print_non_ascii(img = image, text = f"Answer : {self.deck_database.decks[self.deck_database.current_index].cards[self.deck_database.decks[self.deck_database.current_index].study_index].back}",bounding_box =  BoundingBox(42, 332, 600, 100), font_size = 35, dimension = (100, 600, 3))
            next_button = cv2.imread(self.NEXT_BUTTON_PATH)
            render_onto_bb(image, BoundingBox (311, 772, 140, 34), next_button)
        if (self.edit_card_page.is_open()):
            image = self.edit_card_page.render(image)
        if (self.at_least_one_card_popup_page.is_open()):
            image = self.at_least_one_card_popup_page.render(image)
        return image
    
    def remove_deck(self):
        if(self.deck_database.decks_length() == 1):
            self.at_least_one_deck_popup_page.open()
            return
        self.register_selected_reward(["remove_deck"])
        self.delete_current_deck_check_popup_page.open()

    def remove_card(self):
        if(self.deck_database.decks[self.deck_database.current_index].deck_length() == 1):
            self.at_least_one_card_popup_page.open()
            return
        self.register_selected_reward(["remove_card"])
        self.deck_database.decks[self.deck_database.current_index].remove_card()
    
    def set_logo_shown(self):
        self.register_selected_reward(["logo_shown", not(self.is_logo_enabled)])
        self.is_logo_enabled = not(self.is_logo_enabled)

    def open_choose_deck_study_page(self):
        self.get_state()[6] = 0
        self.choose_deck_study_page.open()
    
    def open_preferences_page(self):
        self.get_state()[6] = 0
        self.preferences_page.open()

    def study_deck(self) -> int:
        if(self.choose_deck_study_page.current_index is not None and not(self.choose_deck_study_page.add_deck_popup.is_open())
        and not(self.choose_deck_study_page.leads_to_external_website_popup.is_open())):
            self.deck_database.current_index = self.choose_deck_study_page.current_index
            self.choose_deck_study_page.register_selected_reward(["study"])
            self.choose_deck_study_page.close()
            self.study()
    
    def open_switch_profile(self):
        self.get_state()[6] = 0
        self.profile_page.open()
    
    def open_import_deck_page(self):
        self.get_state()[6] = 0
        self.import_deck_page.open()

    def open_export_deck_page(self):
        self.get_state()[6] = 0
        self.export_deck_page.open()

    def open_reset_collection_popup(self):
        self.get_state()[6] = 0
        self.reset_collection_popup_page.open()