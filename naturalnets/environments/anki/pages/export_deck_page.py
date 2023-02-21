import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import EXPORTED_DECKS_PATH, IMAGES_PATH
from naturalnets.environments.anki.deck import DeckDatabase
from naturalnets.environments.anki.pages.main_page_popups.five_decks_popup import FiveDecksPopup
from naturalnets.environments.anki.pages.name_exists_popup import NameExistsPopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem
from naturalnets.environments.gui_app.widgets.button import Button


class ExportDeckPage(Page, RewardElement):
    """
    State description:
    This page is used to convert a deck to a .txt file and save it
    in the predefined path for .txt files. Reset button deletes all
    the decks, cancel button closes the window, export button converts
    the selected item of the dropdown to .txt file
            state[0]: if this window is open
    """

    STATE_LEN = 41
    IMG_PATH = os.path.join(IMAGES_PATH, "export_deck_page.png")

    WINDOW_BB = BoundingBox(210, 200, 380, 278)
    INCLUDE_DD_BB = BoundingBox(324, 250, 224, 24)
    INCLUDE_DD_BB_OFFSET = BoundingBox(324, 274, 224, 24)
    EXPORT_BB = BoundingBox(346, 443, 113, 29)
    CANCEL_BB = BoundingBox(470, 443, 113, 29)
    RESET_BB = BoundingBox(218, 441, 110, 29)
    DECK_TEXT_X = 331
    DECK_TEXT_Y = 265
    DECK_NUMBER_X = 260
    DECK_NUMBER_Y = 320

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        # Current profile to select the deck from
        self.profile_database = ProfileDatabase()
        # Decks of the current profile
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()

        self.current_deck = None
        # Appears when the export path already has 5 decks
        self.five_decks_popup = FiveDecksPopup()
        # Appears when the export path already contains a file with the same name
        self.name_exists_popup = NameExistsPopup()

        self.dropdown_items = []
        # Fills the dropdown with the decks of the profile
        self.initialise_dropdown()

        self.include_dropdown = Dropdown(self.INCLUDE_DD_BB_OFFSET, self.dropdown_items)
        self.export_button = Button(self.EXPORT_BB, self.export_deck)
        self.cancel_button = Button(self.CANCEL_BB, self.close)
        self.reset_exported_decks_button = Button(self.RESET_BB, self.reset_exported_decks)

        self.add_child(self.five_decks_popup)
        self.add_child(self.name_exists_popup)
        self.add_widget(self.include_dropdown)
        self.set_reward_children([self.five_decks_popup, self.name_exists_popup])

    """
    Provide reward for opening/closing the page, selecting dropdown items, exporting a deck and resetting the decks
    """

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "dropdown": {
                "opened": 0,
                "selected": [0, 1, 2, 3, 4]
            },
            "exported": 0,
            "reset": 0
        }

    """
    If dropdown or popup is open delegate the click to it. 
    If the area of dropdown is clicked then open the dropdown.
    Else handle the click with buttons.
    """

    def handle_click(self, click_position: np.ndarray):
        if self.include_dropdown.is_open():
            self.include_dropdown.handle_click(click_position)
        if self.name_exists_popup.is_open():
            self.name_exists_popup.handle_click(click_position)
            return
        if self.five_decks_popup.is_open():
            self.five_decks_popup.handle_click(click_position)
            return
        if self.include_dropdown.get_selected_item() is not None:
            self.current_deck = self.include_dropdown.get_selected_item().get_value().name
            self.register_selected_reward(["dropdown", "selected", self.include_dropdown.get_all_items().index(
                self.include_dropdown.get_selected_item())])
        if self.INCLUDE_DD_BB.is_point_inside(click_position):
            self.register_selected_reward(["dropdown", "opened"])
            self.include_dropdown.open()
            return
        if self.export_button.is_clicked_by(click_position):
            self.export_button.handle_click(click_position)
        elif self.cancel_button.is_clicked_by(click_position):
            self.cancel_button.handle_click(click_position)
        elif self.reset_exported_decks_button.is_clicked_by(click_position):
            self.reset_exported_decks_button.handle_click(click_position)

    """
    Open this page and initialize the dropdown
    """

    def open(self):
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        self.initialise_dropdown()
        self.current_deck = None
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    """
    Close this page
    """

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.current_deck = None
        for child in self.get_children():
            child.close()
        self.get_state()[0] = 0

    """
    Return true if the dropdown is open
    """

    def is_open(self):
        return self.get_state()[0]

    """
    If the number of decks does not exceed 5 and the name of the deck to export does not already exist and
    a dropdown item is selected then convert a deck to a .txt file
    """
    def export_deck(self):
        self.register_selected_reward(["exported"])
        if DeckDatabase.count_number_of_files(EXPORTED_DECKS_PATH) == 5:
            self.five_decks_popup.open()
        elif self.include_dropdown.get_selected_item() is None:
            return
        elif DeckDatabase.is_file_exist(self.include_dropdown.get_selected_item().get_value().name,
                                         EXPORTED_DECKS_PATH):
            self.name_exists_popup.open()
        else:
            DeckDatabase.export_deck(self.include_dropdown.get_selected_item().get_value())
            self.close()

    """
    Render the page with its dropdown or popups if opened
    """
    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img, "" if self.current_deck is None else f"{self.current_deck}", (self.DECK_TEXT_X, self.DECK_TEXT_Y), font_scale=0.4)
        put_text(img, f"Number of exported decks: {DeckDatabase.count_number_of_files(EXPORTED_DECKS_PATH)}",
                 (self.DECK_NUMBER_X, self.DECK_NUMBER_Y), font_scale=0.5)
        if self.five_decks_popup.is_open():
            img = self.five_decks_popup.render(img)
        if self.name_exists_popup.is_open():
            img = self.name_exists_popup.render(img)
        if self.include_dropdown.is_open():
            img = self.include_dropdown.render(img)
        return img

    """
    Initialize the dropdown items according to the present decks of the current profile.
    """
    def initialise_dropdown(self):
        self.dropdown_items = []
        for deck in self.deck_database.get_decks():
            self.dropdown_items.append(DropdownItem(deck, deck.name))
        self.include_dropdown = Dropdown(self.INCLUDE_DD_BB_OFFSET, self.dropdown_items)
    """
    Delete all exported decks
    """
    def reset_exported_decks(self):
        DeckDatabase.reset_exported_decks()
        self.register_selected_reward(["reset"])
