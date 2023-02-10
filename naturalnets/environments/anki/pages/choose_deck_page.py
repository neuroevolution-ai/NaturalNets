from math import floor
import os
import cv2
import numpy as np
from naturalnets.environments.anki.pages.main_page_popups import AddDeckPopup
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button


class ChooseDeckPage(Page, RewardElement):
    """
    Is opened up when user clicks select deck button from add card page.
    By clicking the provided table one can change the deck to add card to.
    State description:
        state[0]: if this window is open
        state[i]: i-th menu item of the profiles bounding-box (6 > i > 0)
    """
    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "choose_deck_page.png")

    WINDOW_BB = BoundingBox(160, 160, 498, 375)
    CHOOSE_BB = BoundingBox(189, 501, 107, 25)
    ADD_BB = BoundingBox(359, 501, 107, 25)
    CLOSE_BB = BoundingBox(520, 501, 107, 25)
    """
        Singleton design pattern to ensure that at most one
        ChooseDeckPage is present
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ChooseDeckPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        # Profile database to display all the present profiles
        self.profile_database = ProfileDatabase()
        # Deck database to display all the present decks of the profile
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database

        # Popup for adding a new deck.
        self.add_deck_popup = AddDeckPopup()
        self.add_child(self.add_deck_popup)

        # Index of the currently selected deck in range [0..4]
        self.current_index: int = 0

        self.add_button: Button = Button(self.ADD_BB, self.add_deck_popup.open)
        self.choose_button: Button = Button(self.CHOOSE_BB, self.choose_deck)
        self.close_button: Button = Button(self.CLOSE_BB, self.close)

        self.set_reward_children([self.add_deck_popup])

    """
    Provide reward for opening and closing the page, changing the index and choosing a deck
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2, 3, 4],
            "choose_deck": 0
        }

    def open(self):
        self.current_index: int = 0
        self.get_state()[3] = 0
        self.get_state()[2] = 0
        self.get_state()[1] = 0
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.current_index: int = 0
        self.get_state()[3] = 0
        self.get_state()[2] = 0
        self.get_state()[1] = 0
        self.get_state()[0] = 0

    def is_open(self) -> int:
        return self.get_state()[0]

    """
    Each element has the width of 30. calculate_current_bounding_box()
    provides the currently clickable areas varying by the number of
    present decks. If the click_point is within this bounding_box
    then the current_index is modified.
    upper_left_point = (203, 222) is the upper left hand corner
    coordinate of the table.
    """

    def change_current_deck_index(self, click_point: np.ndarray):
        current_bounding_box = self.calculate_current_bounding_box()
        if current_bounding_box.is_point_inside(click_point):
            click_index: int = floor((click_point[1] - 222) / 30)
            if click_index >= self.deck_database.decks_length():
                return
            self.get_state()[self.current_index + 1] = 0
            self.current_index: int = click_index
            self.get_state()[self.current_index + 1] = 1
            self.register_selected_reward(["index", self.current_index])

    """
    Calculate the clickable area of the table depending on the number of
    current decks.
    """
    def calculate_current_bounding_box(self):
        upper_left_point = (203, 222)
        length = 30 * self.deck_database.decks_length()
        current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 412, length)
        return current_bounding_box

    """
    Executed when the user clicks on the choose button. It sets the currently selected deck to the index
    of the choose_deck_page
    """
    def choose_deck(self):
        self.register_selected_reward(["choose_deck"])
        self.deck_database.set_current_index(self.current_index)
        for i in range(1, 6):
            self.get_state()[i] = 0
        self.get_state()[self.current_index + 1] = 1
        self.close()

    """
    Set the current index to 0 to prevent index out of bound
    """
    def reset_index(self):
        self.current_index: int = 0

    """
    Renders the choose deck page with it's add deck popup if open
    """
    def render(self, img: np.ndarray):
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if self.add_deck_popup.is_open():
            img = self.add_deck_popup.render(img)
        put_text(img, f" {self.deck_database.decks[self.current_index].name}", (210, 204), font_scale=0.5)
        for i, deck in enumerate(self.deck_database.decks):
            if self.add_deck_popup.is_open() and i >= 1:
                return img
            put_text(img, f" {deck.name}", (211, 243 + 30 * i), font_scale=0.5)
        return img

    """
    Delegate the click to the add deck popup if open else check if a button is clicked.
    If yes handle it's click.
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        # Updates the deck database of the current profile.
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        if self.add_deck_popup.is_open():
            self.add_deck_popup.handle_click(click_position)
            return
        elif self.add_button.is_clicked_by(click_position):
            self.add_button.handle_click(click_position)
        elif self.choose_button.is_clicked_by(click_position):
            self.choose_button.handle_click(click_position)
        elif self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
        elif self.calculate_current_bounding_box().is_point_inside(click_position):
            self.change_current_deck_index(click_position)
