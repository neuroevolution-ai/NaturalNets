from math import floor
import os
import cv2
import numpy as np
from naturalnets.environments.anki.pages.main_page_popups import AddDeckPopup
from naturalnets.environments.anki.pages.main_page_popups.leads_to_external_website_popup import \
    LeadsToExternalWebsitePopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.widgets.button import Button


class ChooseDeckStudyPage(Page, RewardElement):
    """
    This page enables selecting a deck and switching to the study part of the main
    page. If the selected deck has no cards and one clicks the study button then
    the popup warning that the deck does not have any card appears. However, implementing
    this popup would cause circular dependency between this page and the main page, therefore
    it is implemented in the main page.
    State description:
            state[0]: if this window is open
            state[i]: i-th menu item of the profiles bounding-box (6 > i > 0)
    """

    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "choose_deck_study_page.png")

    WINDOW_BB = BoundingBox(150, 150, 498, 375)
    STUDY_BB = BoundingBox(172, 483, 107, 27)
    ADD_BB = BoundingBox(287, 483, 107, 27)
    CANCEL_BB = BoundingBox(405, 483, 107, 27)
    HELP_BB = BoundingBox(519, 483, 107, 27)

    DECK_BB = BoundingBox(194, 210, 410, 150)
    """
        Singleton design pattern to ensure that at most one
        ChooseDeckStudyPage is present
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ChooseDeckStudyPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        # Popup that appears when the help button is clicked
        self.leads_to_external_website_popup = LeadsToExternalWebsitePopup()

        # Popup that appears when add button is clicked
        self.add_deck_popup = AddDeckPopup()
        self.add_child(self.add_deck_popup)
        self.add_child(self.leads_to_external_website_popup)

        # Index of the currently selected deck
        self.current_index: int = 0

        self.profile_database = ProfileDatabase()
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database

        """
        Study button is implemented in the main page because implementing study function causes circular import
        dependency between main page and this page
        """

        self.add_button: Button = Button(self.ADD_BB, self.add_deck_popup.open)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)
        self.help_button: Button = Button(self.HELP_BB, self.help)
        self.set_reward_children([self.add_deck_popup, self.leads_to_external_website_popup])

    """
    Provide reward for opening/closing a window, changing the index of the selected deck, 
    clicking help button and switching to study session 
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2, 3, 4],
            "help": 0,
            "study": 0
        }

    def open(self):
        self.current_index = 0
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0

    """
    Executed when the help button is clicked.
    """
    def help(self):
        self.leads_to_external_website_popup.open()
        self.register_selected_reward(["help"])

    def is_open(self) -> int:
        return self.get_state()[0]

    """
    Each element has the width of 30. calculate_current_bounding_box()
    provides the currently clickable areas varying by the number of
    present decks. If the click_point is within this bounding_box
    then the current_index is modified.
    upper_left_point = (194, 210) is the upper left hand corner
    coordinate of the table.
    """
    def change_current_deck_index(self, click_point: np.ndarray):
        current_bounding_box = self.calculate_current_bounding_box()
        if current_bounding_box.is_point_inside(click_point):
            click_index: int = floor((click_point[1] - 210) / 30)
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
        upper_left_point = (194, 210)
        length = 29 * self.deck_database.decks_length()
        current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 407, length)
        return current_bounding_box

    """
    Set the current index to 0 to prevent index out of bound
    """
    def reset_index(self):
        self.current_index: int = 0

    """
    Renders the choose deck study page with it's popups if one of them is open
    """
    def render(self, img: np.ndarray):
        # Updates the deck database of the current profile.
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img, f"{self.deck_database.decks[self.current_index].name}", (181, 194), font_scale=0.5)
        if self.leads_to_external_website_popup.is_open():
            self.leads_to_external_website_popup.render(img)
        elif self.add_deck_popup.is_open():
            self.add_deck_popup.render(img)
        # Opened popups do not completely block the background therefore the following if condition is implemented
        for i, deck in enumerate(self.deck_database.decks):
            if ((self.add_deck_popup.is_open() and i >= 1) or (
                    self.leads_to_external_website_popup.is_open() and i >= 3)):
                continue
            put_text(img, f" {deck.name}", (200, 231 + 30 * i), font_scale=0.5)
        return img

    """
    Delegate the click to the add deck popup or leads to external website popup
    if open else check if a button is clicked. If yes handle it's click.
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        # Updates the deck database of the current profile.
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        if self.leads_to_external_website_popup.is_open():
            self.leads_to_external_website_popup.handle_click(click_position)
            return
        if self.add_deck_popup.is_open():
            self.add_deck_popup.handle_click(click_position)
            return
        elif self.add_button.is_clicked_by(click_position):
            self.add_button.handle_click(click_position)
        elif self.cancel_button.is_clicked_by(click_position):
            self.cancel_button.handle_click(click_position)
        elif self.help_button.is_clicked_by(click_position):
            self.help_button.handle_click(click_position)
        elif self.calculate_current_bounding_box().is_point_inside(click_position):
            self.change_current_deck_index(click_position)
