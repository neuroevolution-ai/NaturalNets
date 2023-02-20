from math import floor
import os
from typing import List
import cv2
import numpy as np

import cv2
import numpy as np
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.anki import AddCardPage
from naturalnets.environments.anki import AnkiLoginPage
from naturalnets.environments.anki.pages.main_page_popups.add_deck_popup import AddDeckPopup
from naturalnets.environments.anki import EditCardPage
from naturalnets.environments.anki import ResetCollectionPopup
from naturalnets.environments.anki.pages.main_page_popups.at_least_one_card_popup import AtLeastOneCardPopup
from naturalnets.environments.anki.pages.main_page_popups.at_least_one_deck_popup import AtLeastOneDeckPopup
from naturalnets.environments.anki.pages.main_page_popups.delete_current_deck_check_popup import DeleteCurrentDeckPopup
from naturalnets.environments.anki.pages.main_page_popups.leads_to_external_website_popup import \
    LeadsToExternalWebsitePopup
from naturalnets.environments.anki.pages.main_page_popups.no_card_popup import NoCardPopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import FONTS_PATH, IMAGES_PATH, ANKI_COLOR
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem
from naturalnets.environments.anki import ChooseDeckStudyPage
from naturalnets.environments.anki import CheckMediaPage
from naturalnets.environments.anki import PreferencesPage
from naturalnets.environments.anki import ImportDeckPage
from naturalnets.environments.anki import ProfilePage
from naturalnets.environments.anki import ExportDeckPage
from naturalnets.environments.anki import AboutPage


class MainPage(Page, RewardElement):
    """
    This page provides access to all the sub-parts of the application.
    It is also the part, at which the user starts and proceeds with learning
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

    DECKS_BUTTON_BB = BoundingBox(502, 46, 131, 30)
    CREATE_DECK_BB = BoundingBox(117, 727, 129, 26)
    DELETE_DECK_BB = BoundingBox(345, 727, 129, 26)
    IMPORT_FILE_BB = BoundingBox(583, 727, 129, 26)

    STUDY_BB = BoundingBox(342, 464, 129, 26)
    ADD_CARD_BB = BoundingBox(331, 49, 129, 26)
    GET_SHARED_BB = BoundingBox(501, 49, 129, 26)
    ANKI_LOGIN_BB = BoundingBox(674, 49, 129, 26)

    FILE_DROPDOWN_BB = BoundingBox(0, 0, 70, 31)
    EDIT_DROPDOWN_BB = BoundingBox(70, 0, 70, 31)
    TOOLS_DROPDOWN_BB = BoundingBox(140, 0, 70, 31)
    HELP_DROPDOWN_BB = BoundingBox(210, 0, 70, 31)

    FILE_DROPDOWN_BB_OFFSET = BoundingBox(0, 35, 100, 28)
    EDIT_DROPDOWN_BB_OFFSET = BoundingBox(71, 35, 100, 28)
    TOOLS_DROPDOWN_BB_OFFSET = BoundingBox(142, 35, 100, 28)
    HELP_DROPDOWN_BB_OFFSET = BoundingBox(212, 35, 100, 28)

    EDIT_BB = BoundingBox(145, 749, 85, 24)
    SHOW_ANSWER_NEXT_BB = BoundingBox(329, 749, 158, 24)
    REMOVE_BB = BoundingBox(570, 750, 116, 24)

    BOOK_LOGO = BoundingBox(657, 450, 128, 128)
    ITEM_WIDTH = 39
    ITEM_LENGTH = 614
    UPPER_X = 110
    UPPER_Y = 243
    CURRENT_PROFILE_X = 5
    CURRENT_PROFILE_Y = 162
    CURRENT_DECK_X = 236
    CURRENT_DECK_Y = 162
    CURRENT_ACCOUNT_X = 566
    CURRENT_ACCOUNT_Y = 162
    DECKS_X = 126
    DECKS_Y = 271
    """
    Singleton design pattern to ensure that at most one
    MainPage is present
    """
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MainPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        # All the pages that can be directly accessed from the main page
        self.profile_page = ProfilePage()
        self.import_deck_page = ImportDeckPage()
        self.export_deck_page = ExportDeckPage()
        self.check_media_page = CheckMediaPage()
        self.preferences_page = PreferencesPage()
        self.about_page = AboutPage()
        self.add_card_page = AddCardPage()
        self.anki_login = AnkiLoginPage()
        self.add_deck_popup_page = AddDeckPopup()
        self.edit_card_page = EditCardPage()

        # Profile database to access the currently active profile
        self.profile_database = ProfileDatabase()
        # Deck database to fetch the decks of a profile
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()

        # Popups that can be opened from the main page
        self.leads_to_external_website_popup_page = LeadsToExternalWebsitePopup()
        self.delete_current_deck_check_popup_page = DeleteCurrentDeckPopup()
        self.at_least_one_deck_popup_page = AtLeastOneDeckPopup()
        self.reset_collection_popup_page = ResetCollectionPopup()
        self.no_card_popup_page = NoCardPopup()
        self.at_least_one_card_popup_page = AtLeastOneCardPopup()
        self.choose_deck_study_page = ChooseDeckStudyPage()

        self.pages: List[Page] = [self.profile_page, self.import_deck_page, self.export_deck_page,
                                  self.choose_deck_study_page,
                                  self.check_media_page, self.preferences_page, self.about_page, self.add_card_page,
                                  self.anki_login, self.add_deck_popup_page,
                                  self.edit_card_page, self.leads_to_external_website_popup_page,
                                  self.at_least_one_deck_popup_page, self.reset_collection_popup_page,
                                  self.no_card_popup_page, self.at_least_one_card_popup_page,
                                  self.delete_current_deck_check_popup_page]

        self.add_children([self.profile_page, self.import_deck_page, self.export_deck_page,
                           self.choose_deck_study_page, self.check_media_page, self.preferences_page, self.about_page,
                           self.add_card_page, self.add_deck_popup_page, self.edit_card_page, self.anki_login,
                           self.leads_to_external_website_popup_page,
                           self.delete_current_deck_check_popup_page, self.at_least_one_deck_popup_page,
                           self.reset_collection_popup_page, self.no_card_popup_page,
                           self.at_least_one_card_popup_page, self.choose_deck_study_page, self.preferences_page])

        # Set the dd items with their actions
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

        self.show_book_logo_ddi = DropdownItem("Book Logo", "Book Logo")
        self.show_book_logo_ddi.set_click_action(self.set_logo_shown)

        self.guide_ddi = DropdownItem("Guide", "Guide")
        self.guide_ddi.set_click_action(self.leads_to_external_website_popup_page.open)
        self.support_ddi = DropdownItem("Support", "Support")
        self.support_ddi.set_click_action(self.leads_to_external_website_popup_page.open)
        self.about_ddi = DropdownItem("About Page", "About Page")
        self.about_ddi.set_click_action(self.about_page.open)

        # Create the dropdowns and add them to a list of dropdowns
        self.file_dropdown = Dropdown(self.FILE_DROPDOWN_BB_OFFSET,
                                      [self.switch_profile_ddi, self.import_ddi, self.export_ddi, self.exit_ddi])
        self.edit_dropdown = Dropdown(self.EDIT_DROPDOWN_BB_OFFSET, [self.show_book_logo_ddi])
        self.tools_dropdown = Dropdown(self.TOOLS_DROPDOWN_BB_OFFSET,
                                       [self.study_deck_ddi, self.check_media_ddi, self.preferences_ddi])
        self.help_dropdown = Dropdown(self.HELP_DROPDOWN_BB_OFFSET, [self.guide_ddi, self.support_ddi, self.about_ddi])
        self.dropdowns: List[Dropdown] = [self.file_dropdown, self.edit_dropdown, self.tools_dropdown,
                                          self.help_dropdown]
        # The currently opened dropdown
        self.opened_dd = None
        self.add_widget(self.file_dropdown)
        self.add_widget(self.edit_dropdown)
        self.add_widget(self.tools_dropdown)
        self.add_widget(self.help_dropdown)

        self.decks_button = Button(self.DECKS_BUTTON_BB, self.stop_study)
        self.edit_button = Button(self.EDIT_BB, self.edit_card_page.open)
        self.study_button: Button = Button(self.STUDY_BB, self.study)
        self.add_card_button: Button = Button(self.ADD_CARD_BB, self.add_card)
        self.sync_button: Button = Button(self.ANKI_LOGIN_BB, self.login)
        self.get_shared_button: Button = Button(self.GET_SHARED_BB, self.leads_to_external_website_popup_page.open)
        self.create_deck_button: Button = Button(self.CREATE_DECK_BB, self.create_deck)
        self.import_file_button: Button = Button(self.IMPORT_FILE_BB, self.import_file)
        self.show_answer_button = Button(self.SHOW_ANSWER_NEXT_BB, self.show_answer)
        self.remove_button = Button(self.REMOVE_BB, self.remove_card)
        self.next_button = Button(self.SHOW_ANSWER_NEXT_BB, self.next_card)
        self.delete_button = Button(self.DELETE_DECK_BB, self.remove_deck)
        # This button is actually part of the choose deck study page but the button and the click action is handled here
        self.study_button_study_deck: Button = Button(self.choose_deck_study_page.STUDY_BB, self.study_deck)

        self.main_page_widgets = [self.add_card_button, self.sync_button, self.study_button, self.get_shared_button,
                                  self.create_deck_button, self.import_file_button, self.delete_button]

        self.study_page_widgets = [self.add_card_button, self.decks_button, self.sync_button, self.edit_button,
                                   self.show_answer_button, self.remove_button, self.next_button]

        self.dropdown_bbs = [self.FILE_DROPDOWN_BB, self.EDIT_DROPDOWN_BB, self.TOOLS_DROPDOWN_BB,
                             self.HELP_DROPDOWN_BB]

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

        self.set_reward_children(
            [self.profile_page, self.anki_login, self.add_deck_popup_page, self.leads_to_external_website_popup_page,
             self.add_card_page, self.import_deck_page, self.delete_current_deck_check_popup_page,
             self.at_least_one_deck_popup_page,
             self.reset_collection_popup_page, self.edit_card_page, self.no_card_popup_page,
             self.at_least_one_card_popup_page, self.about_page,
             self.check_media_page, self.choose_deck_study_page, self.preferences_page, self.profile_page,
             self.export_deck_page, self.preferences_page, self.edit_card_page, self.add_card_page])
        # Decides if the anki logo is shown
        self.is_logo_enabled = False

    """
    Provide reward for opening/closing the main window, proceeding with learning, opening dropdowns
    removing card and deck and enabling/disabling anki logo
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "next_card": 0,
            "show_answer": 0,
            "decks": [0, 1, 2, 3, 4],
            "file_dropdown": {
                "opened": 0,
                "selected": ["Switch Profile", "Import", "Export", "Exit"]
            },
            "edit_dropdown": {
                "opened": 0,
                "selected": ["Book Logo"]
            },
            "tools_dropdown": {
                "opened": 0,
                "selected": ["Study Deck", "Check Media", "Preferences"]
            },
            "help": {
                "opened": 0,
                "selected": ["Guide", "Support", "About Page"]
            },
            "study": 0,
            "remove_card": 0,
            "remove_deck": 0,
            "stop_study": 0,
            "logo_shown": [True, False]
        }
    """
    Return the index of a dropdown
    """
    def get_dropdown_index(self):
        for i, dropdown in enumerate(self.dropdowns):
            if dropdown.get_current_value() == self.opened_dd:
                return i
    """
    Delegate the click to a page if one is open else check if a dropdown is open and then delegate click to it
    else check if the state of get_state()[6] == 0 indicating learning is not active and table for decks is clicked
    then handle the click of changing the active deck. Else if the click lies within the bounding box of a dropdown
    then the dropdown is going to be opened. Else the click actions of widgets are handled 
    according to the states get_state()[i] i = {6,7}.
    """
    def handle_click(self, click_position: np.ndarray):
        # Update the current deck database
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        if self.study_button_study_deck.is_clicked_by(click_position) and self.profile_page.is_open():
                self.study_button_study_deck.handle_click(click_position)
        for page in self.pages:
            if page.is_open():
                page.handle_click(click_position)
                return
        
        if self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)
            current_value = self.opened_dd.get_current_value()
            self.opened_dd.close()
            if current_value is not None:
                self.register_selected_reward([self.dropdowns_to_str[self.opened_dd], "selected", current_value])
            self.opened_dd = None
            return

        elif self.DECKS_BB.is_point_inside(click_position) and self.get_state()[6] == 0:
            self.change_current_deck_index(click_position)
            return

        for bounding_box in self.dropdown_bbs:
            if bounding_box.is_point_inside(click_position):
                self.bounding_boxes_to_dropdowns[bounding_box].handle_click(click_position)
                if self.bounding_boxes_to_dropdowns[bounding_box].is_open():
                    self.opened_dd = self.bounding_boxes_to_dropdowns[bounding_box]
                    self.register_selected_reward(
                        [self.dropdowns_to_str[self.bounding_boxes_to_dropdowns[bounding_box]], "opened"])

        if self.get_state()[6] == 0:
            for widget in self.main_page_widgets:
                if widget.is_clicked_by(click_position):
                    widget.handle_click(click_position)
                    return

        elif self.get_state()[7] == 0:
            for widget in self.study_page_widgets:
                if widget is self.next_button:
                    pass
                elif widget.is_clicked_by(click_position):
                    widget.handle_click(click_position)
                    return

        elif self.get_state()[7] == 1:
            for widget in self.study_page_widgets:
                if widget is self.show_answer_button:
                    pass
                elif widget.is_clicked_by(click_position):
                    widget.handle_click(click_position)
                    return
    """
    Opens the add card page 
    """
    def add_card(self):
        self.get_state()[6] = 0
        self.add_card_page.open()

    """
    Opens the anki login page 
    """
    def login(self):
        self.get_state()[6] = 0
        self.anki_login.open()

    """
    Opens the add deck popup page 
    """
    def create_deck(self):
        self.add_deck_popup_page.open()

    """
    Opens the import deck page
    """
    def import_file(self):
        self.get_state()[6] = 0
        self.import_deck_page.open()

    """
    Each element has the width of 39. calculate_current_bounding_box()
    provides the currently clickable areas varying by the number of
    present decks. If the click_point is within this bounding_box
    then the current_index is modified.
    upper_left_point = (110, 243) is the upper left hand corner
    coordinate of the table.
    """
    def change_current_deck_index(self, click_point: np.ndarray):
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        current_bounding_box = self.calculate_current_bounding_box()
        if current_bounding_box.is_point_inside(click_point):
            click_index: int = floor((click_point[1] - self.UPPER_Y) / self.ITEM_WIDTH)
            if click_index >= self.deck_database.decks_length():
                return
            self.get_state()[self.deck_database.get_current_index() + 1] = 0
            self.deck_database.set_current_index(click_index)
            self.get_state()[click_index + 1] = 1
            self.register_selected_reward(["decks", click_index])

    """
    Calculate the clickable area of the table depending on the number of
    current decks.
    """
    def calculate_current_bounding_box(self):
        upper_left_point = (self.UPPER_X, self.UPPER_Y)
        length = self.ITEM_WIDTH * self.deck_database.decks_length()
        current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], self.ITEM_LENGTH, length)
        return current_bounding_box
    """
    Opens the main page
    """
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    """
    Closes the main page
    """
    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])
    """
    Returns true if this page is open
    """
    def is_open(self):
        return self.get_state()[0]

    """
    Switches to the learning session if at least one card of the current card is present.
    Else no card popup is going to be opened
    """
    def study(self):
        if len(self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()) == 0:
            self.no_card_popup_page.open()
        else:
            self.register_selected_reward(["study"])
            self.get_state()[6] = 1
            self.get_state()[7] = (
                1 if self.deck_database.get_decks()[self.deck_database.get_current_index()].get_is_answer_shown() else 0)
    """
    Switches back to the main page
    """
    def stop_study(self):
        self.register_selected_reward(["stop_study"])
        self.get_state()[6] = 0

    """
    Iterates to the next card of the current deck
    """
    def next_card(self):
        self.get_state()[7] = 0
        self.deck_database.get_decks()[self.deck_database.get_current_index()].get_is_answer_shown = False
        self.register_selected_reward(["next_card"])
        self.deck_database.get_decks()[self.deck_database.get_current_index()].increment_study_index()
    """
    Specifies if the active deck shows the answer
    """
    def show_answer(self):
        self.deck_database.get_decks()[self.deck_database.get_current_index()].get_is_answer_shown = True
        self.get_state()[7] = 1
        self.register_selected_reward(["show_answer"])
    """
    Render the main page according to whether learning session is active or not
    """
    def render(self, img: np.ndarray):
        # Updates the deck database
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        if self.get_state()[6] == 1:
            img = self.render_study_page(img)
        elif self.get_state()[6] == 0:
            img = self.render_deck_page(img)
        img = self.render_onto_current(img)
        return img
    """
    Renders an open page,dropdown or popup on to the current page
    """
    def render_onto_current(self, img: np.ndarray):
        for page in self.pages:
            if page.is_open():
                img = page.render(img)
        if self.opened_dd is not None:
            img = self.opened_dd.render(img)
        return img
    """
    Renders the image of the page that holds the table for present decks
    """
    def render_deck_page(self, img: np.ndarray):
        frame = cv2.imread(self.IMG_PATH)
        render_onto_bb(img, self.WINDOW_BB, frame)
        
        book_logo = cv2.imread(os.path.join(IMAGES_PATH, "book_logo.png"))
            
        if self.is_logo_enabled:
            render_onto_bb(img, self.BOOK_LOGO, book_logo)
        if self.profile_page.get_current_profile() is not None:
            put_text(img,
                     f"Current profile: {self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_name()}",
                     (self.CURRENT_PROFILE_X, self.CURRENT_PROFILE_Y), font_scale=0.5)

        put_text(img, f"Current deck: {self.deck_database.get_decks()[self.deck_database.get_current_index()].get_name()}",
                     (self.CURRENT_DECK_X, self.CURRENT_DECK_Y), font_scale=0.5)

        if self.anki_login.get_current_account() is not None:
            put_text(img, f"Current account: {self.anki_login.get_current_account().get_account_name()}", (self.CURRENT_ACCOUNT_X, self.CURRENT_ACCOUNT_Y),
                     font_scale=0.5)

        for i, deck in enumerate(self.deck_database.get_decks()):
            put_text(img, deck.name, (self.DECKS_X, self.DECKS_Y + i * self.ITEM_WIDTH), font_scale=0.5)
        return img

    """
    Renders the image of the page for learning
    """
    def render_study_page(self, image: np.ndarray):
        frame = cv2.imread(self.IMG_PATH_STUDY)
        render_onto_bb(image, self.WINDOW_BB, frame)
        decks_button = cv2.imread(self.DECKS_BUTTON_PATH)
        render_onto_bb(image, BoundingBox(501, 46, 132, 30), decks_button)
        book_logo = cv2.imread(IMAGES_PATH + "book_logo.png")
        if self.is_logo_enabled:
            render_onto_bb(image, self.BOOK_LOGO, book_logo)
        put_text(image, f"Current deck: {self.deck_database.get_decks()[self.deck_database.get_current_index()].name}", (484, 142),
                 font_scale=0.5)
        put_text(image,
                 f"Current card number: {self.deck_database.get_decks()[self.deck_database.get_current_index()].study_index + 1}",
                 (484, 172), font_scale=0.5)
        put_text(image, f"Number of cards: {self.deck_database.get_decks()[self.deck_database.get_current_index()].deck_length()}",
                 (484, 202), font_scale=0.5)
        MainPage.print_non_ascii(img=image,
                        text=f"Question : {self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()[self.deck_database.get_decks()[self.deck_database.get_current_index()].study_index].get_front()}",
                        bounding_box=BoundingBox(42, 232, 600, 100), font_size=35, dimension=(100, 600, 3))
        if self.leads_to_external_website_popup_page.is_open():
            image = self.leads_to_external_website_popup_page.render(image)
        if self.get_state()[7] == 1:
            MainPage.print_non_ascii(img=image,
                            text=f"Answer : {self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()[self.deck_database.get_decks()[self.deck_database.get_current_index()].study_index].get_back()}",
                            bounding_box=BoundingBox(42, 332, 600, 100), font_size=35, dimension=(100, 600, 3))
            next_button = cv2.imread(self.NEXT_BUTTON_PATH)
            render_onto_bb(image, BoundingBox(327, 747, 164, 30), next_button)
        if self.edit_card_page.is_open():
            image = self.edit_card_page.render(image)
        if self.at_least_one_card_popup_page.is_open():
            image = self.at_least_one_card_popup_page.render(image)
        return image

    """
    If the number of decks is 1 then at least one deck popup is shown else the deck is deleted
    """
    def remove_deck(self):
        if self.deck_database.decks_length() == 1:
            self.at_least_one_deck_popup_page.open()
            return
        self.register_selected_reward(["remove_deck"])
        self.delete_current_deck_check_popup_page.open()

    """
    If the number of decks is 1 then at least one card popup is shown else the deck is deleted
    """
    def remove_card(self):
        if self.deck_database.get_decks()[self.deck_database.get_current_index()].deck_length() == 1:
            self.at_least_one_card_popup_page.open()
            return
        self.register_selected_reward(["remove_card"])
        self.deck_database.get_decks()[self.deck_database.get_current_index()].remove_card()
    """
    Negate the boolean if the anki logo is shown
    """
    def set_logo_shown(self):
        self.register_selected_reward(["logo_shown", not self.is_logo_enabled])
        self.is_logo_enabled = not self.is_logo_enabled
    """
    Opens choose deck study page
    """
    def open_choose_deck_study_page(self):
        self.get_state()[6] = 0
        self.choose_deck_study_page.open()

    """
    Opens preferences page
    """
    def open_preferences_page(self):
        self.get_state()[6] = 0
        self.preferences_page.open()

    """
    Check if the condition for starting a study is satisfied and if so switch to a study session
    """
    def study_deck(self):
        if (self.choose_deck_study_page.get_current_index() is not None and not (
            self.choose_deck_study_page.add_deck_popup.is_open())
                and not (self.choose_deck_study_page.leads_to_external_website_popup.is_open())):
            self.deck_database.get_current_index = self.choose_deck_study_page.get_current_index()
            self.choose_deck_study_page.register_selected_reward(["study"])
            self.choose_deck_study_page.close()
            self.study()

    """
    Opens profile page
    """
    def open_switch_profile(self):
        self.get_state()[6] = 0
        self.profile_page.open()

    """
    Opens import deck page
    """
    def open_import_deck_page(self):
        self.get_state()[6] = 0
        self.import_deck_page.open()

    """
    Opens export deck page
    """
    def open_export_deck_page(self):
        self.get_state()[6] = 0
        self.export_deck_page.open()

    """
    Opens reset collection popup
    """
    def open_reset_collection_popup(self):
        self.get_state()[6] = 0
        self.reset_collection_popup_page.open()


    def print_non_ascii(img: np.ndarray, text: str, bounding_box: BoundingBox, font_size: int,
                        dimension: Tuple[int, int, int]):   
        image = np.zeros(dimension, dtype=np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image)
        for x in range(pil_image.width):
            for y in range(pil_image.height):
                pil_image.putpixel((x, y), ANKI_COLOR)
        draw = ImageDraw.Draw(pil_image)
        font = ImageFont.truetype(FONTS_PATH, font_size)
        draw.text((5, 5), text, fill="black", font=font)
        image = np.asarray(pil_image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        render_onto_bb(img, bounding_box, image)
        return img
