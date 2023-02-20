from math import floor
import os
import cv2
import numpy as np
from naturalnets.environments.anki import NameExistsPopup
from naturalnets.environments.anki.deck import DeckDatabase
from naturalnets.environments.anki.pages.main_page_popups import FiveDecksPopup
from naturalnets.environments.anki.pages.main_page_popups.leads_to_external_website_popup \
    import LeadsToExternalWebsitePopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH, PREDEFINED_DECKS_PATH
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb

class ImportDeckPage(Page, RewardElement):
    """
    State description:
            state[0]: if this window is open
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "import_deck_page.png")

    WINDOW_BB = BoundingBox(70, 60, 689, 584)
    SELECT_DECK_BB = BoundingBox(568, 107, 127, 25)
    IMPORT_BB = BoundingBox(342, 595, 96, 25)
    CLOSE_BB = BoundingBox(488, 595, 98, 25)
    HELP_BB = BoundingBox(625, 595, 98, 25)
    CURRENT_DECK_NAME_X = 95
    CURRENT_DECK_NAME_Y = 120
    """
    Singleton design pattern to ensure that at most one
    ImportDeckPage is present
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ImportDeckPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):

        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.import_deck_popup = ImportDeckSelectPage()
        self.name_exists_popup = NameExistsPopup()
        self.five_decks_popup = FiveDecksPopup()
        self.leads_to_external_website_popup = LeadsToExternalWebsitePopup()

        self.add_children([self.import_deck_popup, self.name_exists_popup,
                           self.five_decks_popup, self.leads_to_external_website_popup])
        # Profile database to fetch the currently active profile
        self.profile_database = ProfileDatabase()
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()

        self.select_deck_button = Button(self.SELECT_DECK_BB, self.select_deck_popup)
        self.import_button = Button(self.IMPORT_BB, self.import_deck)
        self.close_button = Button(self.CLOSE_BB, self.close)
        self.help_button = Button(self.HELP_BB, self.help)

        self.set_reward_children([self.leads_to_external_website_popup, self.import_deck_popup,
                                  self.five_decks_popup, self.name_exists_popup])

    """
    Provide reward for opening/closing this page, clicking help button and importing a deck 
    """

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "help": 0,
            "import": 0
        }

    """
    Delegate the click to a popup if open else handle click by buttons
    """

    def handle_click(self, click_position: np.ndarray) -> None:
        # Update the current deck database
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        if self.leads_to_external_website_popup.is_open():
            self.leads_to_external_website_popup.handle_click(click_position)
            return
        if self.import_deck_popup.is_open():
            self.import_deck_popup.handle_click(click_position)
            return
        if self.five_decks_popup.is_open():
            self.five_decks_popup.handle_click(click_position)
            return
        if self.name_exists_popup.is_open():
            self.name_exists_popup.handle_click(click_position)
            return
        if self.select_deck_button.is_clicked_by(click_position):
            self.select_deck_button.handle_click(click_position)
        elif self.import_button.is_clicked_by(click_position):
            self.import_button.handle_click(click_position)
        elif self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
        elif self.help_button.is_clicked_by(click_position):
            self.help_button.handle_click(click_position)

    """
    Opens this page
    """

    def open(self):
        self.register_selected_reward(["window", "open"])
        self.get_state()[0] = 1

    """
    Opens the choose deck page to change the currently selected deck
    """

    def select_deck_popup(self):
        self.import_deck_popup.reset_current_index()
        self.import_deck_popup.open()

    """
    Closes this page
    """

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0

    """
    Returns true if this page is open
    """

    def is_open(self):
        return self.get_state()[0]

    """
    Click action of help button
    """

    def help(self):
        self.leads_to_external_website_popup.open()
        self.register_selected_reward(["help"])

    """
    Imports deck if the number of decks does not exceed 5 and the name of the deck does not exist 
    and the deck to import is set.
    """

    def import_deck(self):
        if self.import_deck_popup.get_current_import_name() is None:
            return
        elif not (self.deck_database.is_deck_length_allowed()):
            self.five_decks_popup.open()
            return
        elif self.deck_database.is_included(self.import_deck_popup.get_current_import_name()):
            self.name_exists_popup.open()
            return
        else:
            self.deck_database.import_deck(self.import_deck_popup.get_current_import_name())
            self.register_selected_reward(["import"])
            self.close()

    """
    Render this page with it's popups if opened.
    """

    def render(self, img: np.ndarray):
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if self.import_deck_popup.get_current_import_name() is not None:
            put_text(img, f"Current import deck: {self.import_deck_popup.get_current_import_name()}", (self.CURRENT_DECK_NAME_X, self.CURRENT_DECK_NAME_Y),
                     font_scale=0.5)
        if self.import_deck_popup.is_open():
            img = self.import_deck_popup.render(img)
        elif self.leads_to_external_website_popup.is_open():
            img = self.leads_to_external_website_popup.render(img)
        elif self.five_decks_popup.is_open():
            img = self.five_decks_popup.render(img)
        elif self.name_exists_popup.is_open():
            img = self.name_exists_popup.render(img)
        return img


class ImportDeckSelectPage(Page, RewardElement):
    """
    Select the deck to import. Decks are predefined:
    Dutch_numbers_0-100
    German_numbers_0-100
    English_numbers_0-100
    State description:
            state[0]: if this window is open
            state[i]: if the i-th item is selected i = {1,2,3}
    """
    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "import_deck_select_page.png")

    WINDOW_BB = BoundingBox(150, 150, 499, 373)
    CHOOSE_BB = BoundingBox(318, 488, 98, 24)
    CLOSE_BB = BoundingBox(432, 488, 96, 24)
    HELP_BB = BoundingBox(543, 488, 98, 24)
    DECK_BB = BoundingBox(182, 202, 420, 150)
    SELECT_DECK_X = 183
    SELECT_DECK_Y = 205
    ITEM_LENGTH = 30
    ITEM_WIDTH = 421
    CURRENT_DECK_X = 189
    CURRENT_DECK_Y = 192
    FIRST_DECK_X = 191
    FIRST_DECK_Y = 225

    """
        Singleton design pattern to ensure that at most one
        ImportDeckSelectPage is present
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ImportDeckSelectPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.current_index = 0
        self.leads_to_external_website_popup = LeadsToExternalWebsitePopup()
        self.current_import_name = None
        # Profile database to fetch current profile
        self.profile_database = ProfileDatabase()
        # Deck database to fetch the decks of the current profile
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()

        self.choose_button: Button = Button(self.CHOOSE_BB, self.set_import_name)
        self.help_button: Button = Button(self.HELP_BB, self.help)
        self.close_button: Button = Button(self.CLOSE_BB, self.close)

        self.set_reward_children([self.leads_to_external_website_popup])

    """
        Reward the agent for opening/closing the page, changing the selected deck, clicking the help button,
        changing the deck to import
    """

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2],
            "help": 0,
            "import_name": 0
        }

    """
    Delegate the click to the popup if open else handle click by buttons
    """

    def handle_click(self, click_position: np.ndarray):
        if self.leads_to_external_website_popup.is_open():
            self.leads_to_external_website_popup.handle_click(click_position)
            return
        if self.choose_button.is_clicked_by(click_position):
            self.choose_button.handle_click(click_position)
        elif self.help_button.is_clicked_by(click_position):
            self.help_button.handle_click(click_position)
        elif self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
        elif self.calculate_current_bounding_box().is_point_inside(click_position):
            self.change_current_deck_index(click_position)

    """
    Opens this popup
    """

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    """
    Closes this popup
    """

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    """
    Click action of help button
    """

    def help(self):
        self.leads_to_external_website_popup.open()
        self.register_selected_reward(["help"])

    """
    Returns true if the popup is open
    """

    def is_open(self) -> int:
        return self.get_state()[0]

    """
    Checks if the click_point lies within the current_bounding_box if yes current_index
    is changed
    """
    def change_current_deck_index(self, click_point: np.ndarray):
        current_bounding_box = ImportDeckSelectPage.calculate_current_bounding_box()
        if current_bounding_box.is_point_inside(click_point):
            click_index: int = floor((click_point[1] - self.SELECT_DECK_Y) / self.ITEM_LENGTH)
            if click_index >= self.deck_database.decks_length():
                return
            self.get_state()[self.current_index + 1] = 0
            self.current_index: int = click_index
            self.get_state()[self.current_index + 1] = 1
            self.register_selected_reward(["index", click_index])
    """
    Calculate the clickable area of the import table
    """

    def calculate_current_bounding_box(self):
        upper_left_point = (self.SELECT_DECK_X, self.SELECT_DECK_Y)
        length = self.ITEM_LENGTH * DeckDatabase.count_number_of_files(PREDEFINED_DECKS_PATH)
        current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], self.ITEM_WIDTH, length)
        return current_bounding_box

    """
    Changes the name of the deck to import according to current_index
    """
    def set_import_name(self):
        self.register_selected_reward(["import_name"])
        self.current_import_name = self.deck_database.get_deck_import_names()[self.current_index]
        self.close()
    """
    Sets the current_index to 0
    """
    def reset_current_index(self):
        self.current_index = 0
    """
    Renders the image of this popup
    """
    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if self.leads_to_external_website_popup.is_open():
            img = self.leads_to_external_website_popup.render(img)
        if self.deck_database.get_deck_import_names()[self.current_index] is not None:
            put_text(img, f"{self.deck_database.get_deck_import_names()[self.current_index]}", (self.CURRENT_DECK_X, self.CURRENT_DECK_Y), font_scale=0.5)
        for i, deck_name in enumerate(self.deck_database.get_deck_import_names()):
            put_text(img, f"{deck_name}", (self.FIRST_DECK_X, self.FIRST_DECK_Y + self.ITEM_LENGTH * i), font_scale=0.5)
        return img

    def get_current_import_name(self):
        return self.current_import_name