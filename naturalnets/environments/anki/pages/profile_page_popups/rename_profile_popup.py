import os
import cv2

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.pages.name_exists_popup import NameExistsPopup
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button


class RenameProfilePopup(RewardElement, Page):
    """
    State description:
        Change the name of the currently active profile
        state[0]: if this popup is open
        state[1]: if the text field is filled
    """

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "rename_profile_popup.png")

    WINDOW_BB = BoundingBox(160, 305, 498, 111)
    OK_BB = BoundingBox(451, 381, 82, 24)
    TEXT_BB = BoundingBox(566, 345, 86, 20)
    CANCEL_BB = BoundingBox(549, 381, 101, 24)
    TEXT_X = 191
    TEXT_Y = 359

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        # Database of the profiles
        self.profile_database = ProfileDatabase()
        self.name_exists_popup_page = NameExistsPopup()

        self.profile_iterate_index = 0
        # Currently set string
        self.current_field_string = None

        self.text_button: Button = Button(self.TEXT_BB, self.set_current_field_string)
        self.ok_button: Button = Button(self.OK_BB, self.rename_profile)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)

        self.add_child(self.name_exists_popup_page)
        self.set_reward_children([self.name_exists_popup_page])

    """
    Provide reward for opening/closing this popup, renaming a profile and setting the temporary string
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "profile_name_clipboard": 0,
            "rename": 0
        }

    """
    Execute click action if a button is clicked
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.name_exists_popup_page.is_open():
            self.name_exists_popup_page.handle_click(click_position)
            return
        elif self.text_button.is_clicked_by(click_position):
            self.text_button.handle_click(click_position)
        elif self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
        elif self.cancel_button.is_clicked_by(click_position):
            self.cancel_button.handle_click(click_position)

    """
    Closes this popup
    """
    def close(self):
        self.get_state()[0:2] = 0
        for child in self.get_children():
            child.close()
        self.register_selected_reward(["window", "close"])
        self.current_field_string = None

    """
    Opens this popup
    """
    def open(self):
        self.get_state()[0] = 1
        self.get_state()[1] = 0
        self.register_selected_reward(["window", "open"])

    """
    Sets a profile name
    """
    def set_current_field_string(self):
        self.current_field_string = self.profile_database.get_profile_names()[self.profile_iterate_index]
        self.profile_iterate_index += 1
        self.profile_iterate_index %= 5
        self.register_selected_reward(["profile_name_clipboard"])

    """
    Returns true if this popup is open
    """
    def is_open(self) -> int:
        return self.get_state()[0]

    """
    If the new name is already present then name exists popup appears else the profile name is changed.
    """
    def rename_profile(self):
        if self.current_field_string is None:
            return
        if self.profile_database.is_included(self.current_field_string):
            self.name_exists_popup_page.open()
        else:
            self.profile_database.rename_profile(self.current_field_string)
            self.register_selected_reward(["rename"])
            self.close()

    """
    Renders the image of this popup
    """
    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if self.name_exists_popup_page.is_open():
            img = self.name_exists_popup_page.render(img)
        put_text(img, "" if self.current_field_string is None else self.current_field_string,
                 (self.TEXT_X, self.TEXT_Y), font_scale=0.5)
        return img
