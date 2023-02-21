import os
import cv2
import numpy as np
from naturalnets.environments.anki.pages.main_page_popups.five_decks_popup import FiveDecksPopup
from naturalnets.environments.anki.pages.name_exists_popup import NameExistsPopup
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button


class AddDeckPopup(Page, RewardElement):
    """
    This popup is used to create a new deck.
    Deck names are "Deck Name i" i = {1,..,5}
    Text button assigns a name
    Cancel button closes the window and resets the current name string
    OK button adds the deck iff a name is provided by clicking the text button
    and less than 5 decks are present and the name does not exist
    State description:
            state[0]: if this popup is open
            state[i]: if the text field is filled with input "Deck_name_i"
    """
    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "add_deck_popup.png")

    WINDOW_BB = BoundingBox(150, 250, 498, 109)
    OK_BB = BoundingBox(443, 324, 81, 25)
    CANCEL_BB = BoundingBox(538, 324, 103, 25)
    TEXT_BB = BoundingBox(555, 289, 86, 20)

    TEXT_POSITION_X = 181
    TEXT_POSITION_Y = 302

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        # pops up when five decks are present
        self.five_decks_popup = FiveDecksPopup()
        # pops up when the name of the deck already exists
        self.name_exists_popup = NameExistsPopup()
        # database containing current profiles
        self.profile_database = ProfileDatabase()
        # database containing current decks
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()

        self.add_child(self.five_decks_popup)
        self.add_child(self.name_exists_popup)

        self.deck_iterate_index = 0
        #  temporarily set string
        self.current_field_string = None

        self.ok_button: Button = Button(self.OK_BB, self.add_deck)
        self.text_button: Button = Button(self.TEXT_BB, self.set_deck_name_clipboard)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)

        # set rewards of the popups
        self.set_reward_children([self.name_exists_popup, self.five_decks_popup])

    """
    Provide reward for opening/closing this popup, clicking the text button and adding a new deck successfully
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "set_clipboard": 0,
            "add_new_deck": 0
        }

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.current_field_string = None
        for child in self.get_children():
            child.close()
        self.get_state()[0:6] = 0

    def open(self):
        self.register_selected_reward(["window", "open"])
        self.get_state()[0] = 1
        self.get_state()[1:6] = 0

    """
    Set a deck name
    """
    def set_deck_name_clipboard(self):
        self.register_selected_reward(["set_clipboard"])
        self.current_field_string = self.deck_database.get_deck_names()[self.deck_iterate_index]
        self.get_state()[1 + (self.deck_iterate_index - 1) % 5] = 0
        self.deck_iterate_index += 1
        self.deck_iterate_index %= 5
        self.get_state()[1 + (self.deck_iterate_index - 1) % 5] = 1
        

    def is_open(self):
        return self.get_state()[0]

    """
    Check if there are less than 5 decks and the name does not exist
    then create the deck
    else show the respective popup
    """
    def add_deck(self):
        if self.current_field_string is None:
            return
        elif not (self.deck_database.is_deck_length_allowed()):
            self.five_decks_popup.open()
        elif self.deck_database.is_included(self.current_field_string):
            self.name_exists_popup.open()
        else:
            self.deck_database.create_deck(self.current_field_string)
            self.register_selected_reward(["add_new_deck"])
            self.current_field_string = None
            self.close()
    """
    Render the popup and if one of the warning popups are open render it too
    """
    def render(self, img: np.ndarray):
        # First line synchronizes the self.deck_database attribute with the current database.
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if self.current_field_string is not None:
            put_text(img, f"{self.current_field_string}", (self.TEXT_POSITION_X, self.TEXT_POSITION_Y), font_scale=0.4)
        if self.five_decks_popup.is_open():
            img = self.five_decks_popup.render(img)
        elif self.name_exists_popup.is_open():
            img = self.name_exists_popup.render(img)
        return img
    """
    Execute the click action according to the respective button or popup
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        # First line synchronizes the self.deck_database attribute with the current database.
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        if self.five_decks_popup.is_open():
            self.five_decks_popup.handle_click(click_position)
            return
        elif self.name_exists_popup.is_open():
            self.name_exists_popup.handle_click(click_position)
            return
        elif self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
        elif self.text_button.is_clicked_by(click_position):
            self.text_button.handle_click(click_position)
        elif self.cancel_button.is_clicked_by(click_position):
            self.cancel_button.handle_click(click_position)
