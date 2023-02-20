import os
import cv2

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button


class DeleteCurrentDeckPopup(Page, RewardElement):
    """
    Pops up when the delete deck button from the main
    page is clicked. If the user clicks yes the selected
    deck is going to be deleted if no is clicked then the
    popup will be closed.
    State description:
        state[0]: if this window is open  
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "delete_current_deck_popup.png")

    WINDOW_BB = BoundingBox(130, 270, 530, 113)
    YES_BB = BoundingBox(448, 347, 85, 24)
    NO_BB = BoundingBox(559, 347, 85, 24)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        # Profile database is necessary to fetch the currently active profile
        self.profile_database = ProfileDatabase()
        # Deck database is necessary to fetch the decks of a profile
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        self.yes_button = Button(self.YES_BB, self.remove_deck)
        self.no_button = Button(self.NO_BB, self.close)
    """
    Provide reward for opening and closing the popup and deleting a deck
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "delete_deck": 0
        }
    """
    Check if yes or no button is clicked and if so handle the click
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        # Updates the current deck database.
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].deck_database
        if self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
        elif self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0

    def is_open(self):
        return self.get_state()[0]
    """
    Remove the selected deck from the deck database. Is called when yes button is clicked
    """
    def remove_deck(self):
        self.deck_database.delete_deck(self.deck_database.get_decks()[self.deck_database.get_current_index()].get_name())
        self.close()
        self.register_selected_reward(["delete_deck"])
    """
    Renders the image of the popup
    """
    def render(self, img: np.ndarray):
        # Updates the current deck database.
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img
