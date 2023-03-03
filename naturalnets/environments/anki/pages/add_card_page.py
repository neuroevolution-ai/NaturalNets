import os
import cv2
import numpy as np
from naturalnets.environments.anki import ChooseDeckPage
from naturalnets.environments.anki.pages.main_page_popups.front_and_backside_popup import FrontAndBacksidePopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki import Card


class AddCardPage(Page, RewardElement):
    """
    This page is used to add a card to the current deck.
    When a text button is clicked then a random string of length 10
    is set for the respective area. In order to add a card front- and
    backside fields must be filled. Tag is optional.
    State description:
            state[0]: if this window is open
            state[i]: if the i-th field is filled (4 > i > 0)
    The content of the field has no impact on the logic of app hence it is only important if the
    field is filled
    """

    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "add_card_page.png")

    WINDOW_BB = BoundingBox(130, 120, 566, 456)
    SELECT_BB = BoundingBox(545, 151, 120, 25)
    FRONT_TEXT_BB = BoundingBox(588, 299, 87, 25)
    BACK_TEXT_BB = BoundingBox(588, 407, 87, 25)
    TAGS_TEXT_BB = BoundingBox(588, 494, 87, 25)
    CLOSE_BB = BoundingBox(582, 538, 88, 25)
    ADD_BB = BoundingBox(466, 538, 88, 25)

    DECK_TEXT_X = 277
    DECK_TEXT_Y = 191
    FRONT_TEXT_X = 198
    FRONT_TEXT_Y = 310
    BACK_TEXT_X = 198
    BACK_TEXT_Y = 422
    TAG_TEXT_X = 198
    TAG_TEXT_Y = 507

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        # Temporarily set strings
        self.front_side_clipboard_temporary_string = None
        self.back_side_clipboard_temporary_string = None
        self.tag_clipboard_temporary_string = None

        # Profile database to fetch the current profile
        self.profile_database = ProfileDatabase()
        # Deck database of the current profile to add card to the current deck
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        # Choose deck page enables changing the current deck as well as adding a new deck
        self.choose_deck = ChooseDeckPage()
        # Warning popup that front- and backside strings must be present at the same time to be able to add a new card.
        self.front_and_backside_popup = FrontAndBacksidePopup()
        
        self.front_side_counter = 0
        self.back_side_counter = 0
        self.tag_counter = 0

        self.add_child(self.choose_deck)
        self.add_child(self.front_and_backside_popup)

        self.select_button: Button = Button(self.SELECT_BB, self.select_deck)
        self.front_text_button: Button = Button(self.FRONT_TEXT_BB, self.set_front_side_clipboard)
        self.back_text_button: Button = Button(self.BACK_TEXT_BB, self.set_back_side_clipboard)
        self.tags_text_button: Button = Button(self.TAGS_TEXT_BB, self.set_tag_clipboard)
        self.close_button: Button = Button(self.CLOSE_BB, self.close)
        self.add_button: Button = Button(self.ADD_BB, self.add_card)

        # Set the rewards of the popups
        self.set_reward_children([self.choose_deck, self.front_and_backside_popup])

    """
    Provide reward for opening and closing the page, Setting each text field and adding a card
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "front_side_clipboard": 0,
            "back_side_clipboard": 0,
            "tag_clipboard": 0,
            "add_card": 0
        }

    """
    First check if a popup is open. If yes delegate the click to the popup.
    Else check if a button is clicked and if yes handle it's click
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        # Updates the deck database of the current profile.
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        if self.choose_deck.is_open():
            self.choose_deck.handle_click(click_position)
            return
        if self.front_and_backside_popup.is_open():
            self.front_and_backside_popup.handle_click(click_position)
            return
        elif self.select_button.is_clicked_by(click_position):
            self.select_button.handle_click(click_position)
        elif self.front_text_button.is_clicked_by(click_position):
            self.front_text_button.handle_click(click_position)
        elif self.back_text_button.is_clicked_by(click_position):
            self.back_text_button.handle_click(click_position)
        elif self.tags_text_button.is_clicked_by(click_position):
            self.tags_text_button.handle_click(click_position)
        elif self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
        elif self.add_button.is_clicked_by(click_position):
            self.add_button.handle_click(click_position)

    def open(self):
        self.reset_temporary_strings()
        self.get_state()[0] = 1
        self.get_state()[1:4] = 0
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0:4] = 0
        for child in self.get_children():
            child.close()
        self.reset_temporary_strings()
        self.register_selected_reward(["window", "close"])

    def is_open(self):
        return self.get_state()[0]

    """
    Assign a random string to the front side field
    """
    def set_front_side_clipboard(self):
        self.register_selected_reward(["front_side_clipboard"])
        self.front_side_clipboard_temporary_string = f"Some front side text {self.front_side_counter}"
        self.front_side_counter += 1
        self.get_state()[1] = 1

    """
        Assign a random string to the back side field
    """
    def set_back_side_clipboard(self):
        self.register_selected_reward(["back_side_clipboard"])
        self.back_side_clipboard_temporary_string = f"Some back side text {self.back_side_counter}"
        self.back_side_counter += 1
        self.get_state()[2] = 1

    """
        Assign a random string to the tag field
    """
    def set_tag_clipboard(self):
        self.register_selected_reward(["tag_clipboard"])
        self.tag_clipboard_temporary_string = f"Some tag text {self.tag_counter}"
        self.tag_counter += 1 
        self.get_state()[3] = 1

    """
    Check if the front- and the back side of the card is set
    """
    def is_card_creatable(self):
        return self.back_side_clipboard_temporary_string is not None and self.front_side_clipboard_temporary_string \
            is not None

    """
    Reset the current string configuration
    """
    def reset_temporary_strings(self):
        self.back_side_clipboard_temporary_string = None
        self.front_side_clipboard_temporary_string = None
        self.tag_clipboard_temporary_string = None
        self.get_state()[1:4] = 0

    """
    Checks if the condition for creating a card is satisfied and if yes
    creates a card and adds it to the current deck and resets the string
    configuration. If the condition for creating card is not satisfied then
    the popup warning that both the front- and back side of the card must be
    present is shown.
    """
    def add_card(self):
        if self.is_card_creatable():
            card = Card(self.front_side_clipboard_temporary_string, self.back_side_clipboard_temporary_string,
                        self.tag_clipboard_temporary_string)
            self.deck_database.get_decks()[self.deck_database.get_current_index()].add_card(card)
            self.register_selected_reward(["add_card"])
            self.reset_temporary_strings()
        else:
            self.front_and_backside_popup.open()
    
    """
    Opens up the popup for selecting a deck. Reason for resetting the index of
    the popup to 0 is to prevent index out of range. Suppose the current profile has
    5 decks with index 0 to 4. User clicks the index 4 and then closes the popup.
    Apart from this the user can delete 4 decks. When the user opens up this popup
    again then the index would be out of bound if it wouldn't be set to 0 since it was > 0
    and there is only one deck present of the current profile.
    """
    def select_deck(self):
        self.choose_deck.reset_index()
        self.choose_deck.open()
    
    """
    Renders the add card page with popup or 
    choose deck page if open and current strings if set.
    """
    def render(self, img: np.ndarray):
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        # Render choose deck page if open
        if self.choose_deck.is_open():
            self.choose_deck.render(img)
            return img
        put_text(img, f"{self.deck_database.get_decks()[self.deck_database.get_current_index()].get_name()}",
                 (self.DECK_TEXT_X, self.DECK_TEXT_Y), font_scale=0.5)
        # This popup does not completely block the background therefore backside and tag fields are rendered too
        if self.front_and_backside_popup.is_open():
            self.front_and_backside_popup.render(img)
            if self.back_side_clipboard_temporary_string is not None:
                put_text(img, f"{self.back_side_clipboard_temporary_string}", (self.BACK_TEXT_X, self.BACK_TEXT_Y),
                         font_scale=0.5)
            if self.tag_clipboard_temporary_string is not None:
                put_text(img, f"{self.tag_clipboard_temporary_string}", (self.TAG_TEXT_X, self.TAG_TEXT_Y),
                         font_scale=0.5)
            return img
        # Put the current strings on text fields
        if self.front_side_clipboard_temporary_string is not None:
            put_text(img, f"{self.front_side_clipboard_temporary_string}", (self.FRONT_TEXT_X, self.FRONT_TEXT_Y),
                     font_scale=0.5)
        if self.back_side_clipboard_temporary_string is not None:
            put_text(img, f"{self.back_side_clipboard_temporary_string}", (self.BACK_TEXT_X, self.BACK_TEXT_Y),
                     font_scale=0.5)
        if self.tag_clipboard_temporary_string is not None:
            put_text(img, f"{self.tag_clipboard_temporary_string}", (self.TAG_TEXT_X, self.TAG_TEXT_Y),
                     font_scale=0.5)
        return img
