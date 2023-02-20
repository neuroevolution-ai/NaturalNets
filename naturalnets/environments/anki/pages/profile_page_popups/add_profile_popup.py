import os
import random
import cv2

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.pages.name_exists_popup import NameExistsPopup
from naturalnets.environments.anki.pages.profile_page_popups.five_profiles_popup import FiveProfilesPopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button

class AddProfilePopup(Page, RewardElement):
    """
    Adds a new profile to the present profiles
    State description:
        state[0]: if this popup is open
        state[1]: if the text field is filled
    """
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "add_profile_popup.png")

    WINDOW_BB = BoundingBox(160, 305, 498, 109)
    OK_BB = BoundingBox(451, 381, 82, 24)
    TEXT_BB = BoundingBox(566, 345, 86, 20)
    CANCEL_BB = BoundingBox(549, 381, 101, 24)
    TEXT_X = 191
    TEXT_Y = 359

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        # Popups warning that the profile cannot be created
        self.name_exists_popup = NameExistsPopup()
        self.five_profiles_popup = FiveProfilesPopup()
        # Contains the current profiles
        self.profile_database = ProfileDatabase()
        self.add_child(self.name_exists_popup)
        self.add_child(self.five_profiles_popup)
        # Randomizer for selecting a random name
        self.secure_random = random.SystemRandom()
        self.current_field_string = None

        self.text_button: Button = Button(self.TEXT_BB, self.set_current_field_string)
        self.ok_button: Button = Button(self.OK_BB, self.add_profile)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)

        self.add_children([self.name_exists_popup, self.five_profiles_popup])
        self.set_reward_children([self.name_exists_popup, self.five_profiles_popup])

    """
        Provide reward for opening/closing this popup, setting a profile name and adding profile
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "profile_name_clipboard": 0,
            "add_profile": 0
        }

    """
        Delegate click to the popup if one is open else handle click with the buttons.
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.name_exists_popup.is_open():
            self.name_exists_popup.handle_click(click_position)
            return
        if self.five_profiles_popup.is_open():
            self.five_profiles_popup.handle_click(click_position)
            return
        if self.text_button.is_clicked_by(click_position):
            self.text_button.handle_click(click_position)
        elif self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
        elif self.cancel_button.is_clicked_by(click_position):
            self.cancel_button.handle_click(click_position)

    """
    Close this popup
    """
    def close(self):
        self.get_state()[0:2] = 0
        self.register_selected_reward(["window", "close"])
        for child in self.get_children():
            child.close()
        self.current_field_string = None

    """
    Open this popup
    """
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    """
    Set the current string by randomly selecting a name from the predefined set of names
    """
    def set_current_field_string(self):
        self.get_state()[1] = 1
        self.register_selected_reward(["profile_name_clipboard"])
        self.current_field_string = self.secure_random.choice(self.profile_database.get_profile_names())

    """
    Adds the profile if the current_field_string is set and the max number of decks is not exceeded
    and the name of the profile is not present
    """
    def add_profile(self):
        if self.current_field_string is None:
            return
        elif not (self.profile_database.is_adding_allowed()):
            self.five_profiles_popup.open()
        elif self.profile_database.is_included(self.current_field_string):
            self.name_exists_popup.open()
        else:
            self.profile_database.create_profile(self.current_field_string)
            self.current_field_string = None
            self.register_selected_reward(["add_profile"])
            self.close()
    """
    Renders the image of this popup
    """
    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img, "" if self.current_field_string is None else self.current_field_string, (self.TEXT_X, self.TEXT_Y),
                 font_scale=0.5)
        if self.five_profiles_popup.is_open():
            img = self.five_profiles_popup.render(img)
        if self.name_exists_popup.is_open():
            img = self.name_exists_popup.render(img)
        return img
    """
    Returns true if the popup is open
    """
    def is_open(self) -> int:
        return self.get_state()[0]
