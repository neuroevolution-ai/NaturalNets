import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import FONTS_PATH, IMAGES_PATH, ANKI_COLOR
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
import cv2
import numpy as np
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont

class EditCardPage(RewardElement, Page):
    """
    This page is accessed from a study session by clicking the edit button.
    Clicking the text button edits the content of the card by appending
    " edited" to the string.
    State description:
            state[0]: if this window is open
    """

    IMG_PATH = os.path.join(IMAGES_PATH, "edit_card_page.png")
    STATE_LEN = 1

    WINDOW_BB = BoundingBox(150, 100, 499, 500)
    FRONT_TEXT_BB = BoundingBox(545, 221, 89, 28)
    BACK_TEXT_BB = BoundingBox(545, 353, 89, 28)
    TAGS_TEXT_BB = BoundingBox(545, 483, 89, 28)
    CLOSE_BB = BoundingBox(534, 556, 99, 29)
    FRONT_TEXT_PRINT_BB = BoundingBox(225, 203, 300, 40)
    BACK_TEXT_PRINT_BB = BoundingBox(225, 336, 300, 40)
    TAGS_TEXT_PRINT_BB = BoundingBox(225, 483, 300, 36)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        # Profile database to fetch the currently active profile
        self.profile_database = ProfileDatabase()
        # Deck database to fetch the currently active deck of the current profile
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()

        self.front_text_button: Button = Button(self.FRONT_TEXT_BB, self.front_text_edit)
        self.back_text_button: Button = Button(self.BACK_TEXT_BB, self.back_text_edit)
        self.tags_text_button: Button = Button(self.TAGS_TEXT_BB, self.tags_text_edit)
        self.close_button: Button = Button(self.CLOSE_BB, self.close)
    """
    Handle click of a clicked button
    """
    def handle_click(self, click_position: np.ndarray):
        # Updates the deck database of the current profile.
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        if self.front_text_button.is_clicked_by(click_position):
            self.front_text_button.handle_click(click_position)
        elif self.back_text_button.is_clicked_by(click_position):
            self.back_text_button.handle_click(click_position)
        elif self.tags_text_button.is_clicked_by(click_position):
            self.tags_text_button.handle_click(click_position)
        elif self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)

    """
    Provide reward for opening/closing a window and modifying each field
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "first_field_modified": 0,
            "second_field_modified": 0,
            "tags_field_modified": 0
        }

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0

    def is_open(self):
        return self.get_state()[0]

    """
    Appends " edited" to the front side of the current card 
    """
    def front_text_edit(self):
        if (not (self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()
        [self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].is_front_edited())):
            self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()[
                self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].edit_front()
            self.register_selected_reward(["first_field_modified"])
    """
    Appends " edited" to the back side of the current card 
    """
    def back_text_edit(self):
        if not (self.deck_database.get_decks()[self.deck_database.get_current_index()].cards[self.deck_database.get_decks()
        [self.deck_database.get_current_index()].get_study_index()].is_back_edited()):
            self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()[
                self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].edit_back()
            self.register_selected_reward(["second_field_modified"])
    """
    Appends " edited" to the tags of the current card 
    """

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
    
    def tags_text_edit(self):
        if not (self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()
        [self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].is_tag_edited()):
            self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()[
                self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].edit_tag()
            self.register_selected_reward(["tags_field_modified"])

    """
    Render the edit card page with the content of the card as string.
    """
    def render(self, image: np.ndarray):
        # Updates the deck database of the current profile.
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        to_render = cv2.imread(self._img_path)
        image = render_onto_bb(image, self.get_bb(), to_render)
        if (self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()
        [self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].front is not None):
            EditCardPage.print_non_ascii(img=image,
                            text=f"{self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()[self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].get_front()}",
                            bounding_box=self.FRONT_TEXT_PRINT_BB, font_size=25,
                            dimension=(40, 300, 3))
        if self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()[self.deck_database.get_decks()
        [self.deck_database.get_current_index()]
                .get_study_index()].get_back() is not None:
            EditCardPage.print_non_ascii(img=image,
                            text=f"{self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()[self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].get_back()}",
                            bounding_box=self.BACK_TEXT_PRINT_BB, font_size=25,
                            dimension=(40, 300, 3))
        if (self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()
        [self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].get_tag() is not None):
            EditCardPage.print_non_ascii(img=image,
                            text=f"{self.deck_database.get_decks()[self.deck_database.get_current_index()].get_cards()[self.deck_database.get_decks()[self.deck_database.get_current_index()].get_study_index()].get_tag()}",
                            bounding_box=self.TAGS_TEXT_PRINT_BB, font_size=25,
                            dimension=(36, 300, 3))
        return image

    
