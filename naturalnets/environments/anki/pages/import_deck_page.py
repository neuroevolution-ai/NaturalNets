from math import floor
import os
import cv2
import numpy as np
from naturalnets.environments.anki import NameExistsPopup
from naturalnets.environments.anki.deck import Deck, DeckDatabase
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

        self.profile_database = ProfileDatabase()
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database

        self.select_deck_button = Button(self.SELECT_DECK_BB, self.select_deck_popup)
        self.import_button = Button(self.IMPORT_BB, self.import_deck)
        self.close_button = Button(self.CLOSE_BB, self.close)
        self.help_button = Button(self.HELP_BB, self.help)

        self.set_reward_children([self.leads_to_external_website_popup, self.import_deck_popup,
                                  self.five_decks_popup, self.name_exists_popup])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "help": 0,
            "import": 0
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
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

    def open(self):
        self.register_selected_reward(["window", "open"])
        self.get_state()[0] = 1

    def select_deck_popup(self):
        self.import_deck_popup.reset_current_index()
        self.import_deck_popup.open()

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0

    def is_open(self):
        return self.get_state()[0]

    def help(self):
        self.leads_to_external_website_popup.open()
        self.register_selected_reward(["help"])

    def import_deck(self):
        if self.import_deck_popup.current_import_name is None:
            return
        elif not (self.deck_database.is_deck_length_allowed()):
            self.five_decks_popup.open()
            return
        elif self.deck_database.is_included(self.import_deck_popup.current_import_name):
            self.name_exists_popup.open()
            return
        else:
            self.deck_database.import_deck(self.import_deck_popup.current_import_name)
            self.register_selected_reward(["import"])
            self.close()

    def render(self, img: np.ndarray):
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if self.import_deck_popup.current_import_name is not None:
            put_text(img, f"Current import deck: {self.import_deck_popup.current_import_name}", (95, 120),
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

        self.profile_database = ProfileDatabase()
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database

        self.choose_button: Button = Button(self.CHOOSE_BB, self.set_import_name)
        self.help_button: Button = Button(self.HELP_BB, self.help)
        self.close_button: Button = Button(self.CLOSE_BB, self.close)

        self.set_reward_children([self.leads_to_external_website_popup])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2],
            "help": 0,
            "import_name": 0
        }

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

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def help(self):
        self.leads_to_external_website_popup.open()
        self.register_selected_reward(["help"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def change_current_deck_index(self, click_point: np.ndarray):
        current_bounding_box = self.calculate_current_bounding_box()
        if current_bounding_box.is_point_inside(click_point):
            click_index: int = floor((click_point[1] - 205) / 30)
            if click_index >= self.deck_database.decks_length():
                return
            self.get_state()[self.current_index + 1] = 0
            self.current_index: int = click_index
            self.get_state()[self.current_index + 1] = 1
            self.register_selected_reward(["index", click_index])

    def calculate_current_bounding_box(self):
        upper_left_point = (183, 205)
        length = 30 * DeckDatabase.count_number_of_files(PREDEFINED_DECKS_PATH)
        current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 421, length)
        return current_bounding_box

    def set_import_name(self):
        self.register_selected_reward(["import_name"])
        self.current_import_name = self.deck_database.deck_import_names[self.current_index]
        self.close()

    def reset_current_index(self):
        self.current_index = 0

    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if self.leads_to_external_website_popup.is_open():
            img = self.leads_to_external_website_popup.render(img)
        if self.deck_database.deck_import_names[self.current_index] is not None:
            put_text(img, f"{self.deck_database.deck_import_names[self.current_index]}", (189, 192), font_scale=0.5)
        for i, deck_name in enumerate(self.deck_database.deck_import_names):
            put_text(img, f"{deck_name}", (191, 225 + 30 * i), font_scale=0.5)
        return img
