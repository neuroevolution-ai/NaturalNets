import os
import cv2
import numpy as np

from naturalnets.environments.gui_app.constants import IMAGES_PATH
from naturalnets.environments.password_manager_app.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.page import Page
from naturalnets.environments.password_manager_app.reward_element import RewardElement
from naturalnets.environments.password_manager_app.utils import render_onto_bb
from naturalnets.environments.password_manager_app.widgets.button import Button
from naturalnets.environments.password_manager_app.widgets.check_box import CheckBox
from naturalnets.environments.password_manager_app.widgets.dropdown import Dropdown, DropdownItem


class AddAccount(Page, RewardElement):
    """todo"""

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "account_window/add_account_empty")

    BOUNDING_BOX = BoundingBox(0, 0, 448, 448)

    HIDE_PASSWORD_BB = BoundingBox(0, 0, 448, 448)

    OK_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    CLOSE_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    GENERATE_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    LAUNCH_URL_BUTTON_BB = BoundingBox(0, 0, 448, 448)

    COPY_ACCOUNT_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    COPY_USER_ID_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    COPY_PASSWORD_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    COPY_URL_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    COPY_NOTES_BUTTON_BB = BoundingBox(0, 0, 448, 448)

    PAST_ACCOUNT_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    PAST_USER_ID_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    PAST_PASSWORD_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    PAST_URL_BUTTON_BB = BoundingBox(0, 0, 448, 448)
    PAST_NOTES_BUTTON_BB = BoundingBox(0, 0, 448, 448)

    ACCOUNT_DD_BB = BoundingBox(0, 0, 448, 448)
    USER_ID_DD_BB = BoundingBox(0, 0, 448, 448)
    PASSWORD_DD_BB = BoundingBox(0, 0, 448, 448)
    URL_DD_BB = BoundingBox(0, 0, 448, 448)
    NOTES_DD_BB = BoundingBox(0, 0, 448, 448)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.name_one = DropdownItem("Hanna", "Hanna")
        self.name_two = DropdownItem("Klaus", "Klaus")
        self.name_three = DropdownItem("Mariam", "Mariam")
        self.dropdown_account = Dropdown(self.ACCOUNT_DD_BB, [self.name_one,
                                                   self.name_two,
                                                   self.name_three])
        self.dropdown_user_id = Dropdown(self.USER_ID_DD_BB, [self.name_one,
                                                   self.name_two,
                                                   self.name_three])
        
        self.password_one = DropdownItem("1234", "1234")
        self.password_two = DropdownItem("qwertz", "qwertz")
        self.password_three = DropdownItem("asdf", "asdf")
        self.dropdown_password = Dropdown(self.ACCOUNT_DD_BB, [self.password_one,
                                                   self.password_two,
                                                   self.password_three])
        
        self.dropdown_password.set_selected_item(self.password_one)

        self.dropdown_url = Dropdown(self.ACCOUNT_DD_BB, [self.name_one,
                                                   self.name_two,
                                                   self.name_three])
        self.dropdown_notes = Dropdown(self.ACCOUNT_DD_BB, [self.name_one,
                                                   self.name_two,
                                                   self.name_three])
        
        self.dropdowns = [
            self.dropdown_account,
            self.dropdown_user_id,
            self.dropdown_password,
            self.dropdown_url,
            self.dropdown_notes
        ]

        self.add_widgets(self.dropdowns)
        
        self.checkbox = CheckBox(
            self.HIDE_PASSWORD_BB,
            lambda is_checked: self.set_hide_password(is_checked)
        )

        self.add_widget(self.checkbox)

        self.buttons = [
            Button(self.OK_BUTTON_BB, lambda: self.set_current_page(self.add_account)),
            Button(self.CLOSE_BUTTON_BB, lambda: self.set_current_page(self.edit_account)),
            Button(self.GENERATE_BUTTON_BB, lambda: self.set_current_page(self.confirm_delete_account)),
            Button(self.COPY_ACCOUNT_BUTTON_BB, lambda: self.set_current_page(None)),
            Button(self.COPY_PASSWORD_BUTTON_BB, lambda: self.set_current_page(None)),
            Button(self.LAUNCH_URL_BUTTON_BB, lambda: self.set_current_page(None)),
            Button(self.COPY_USER_ID_BUTTON_BB, lambda: self.set_current_page(self.options)),
            Button(self.COPY_URL_BUTTON_BB, lambda: self.set_current_page(self.database)),
            Button(self.COPY_NOTES_BUTTON_BB, lambda: self.set_current_page(self.account)),
            Button(self.PAST_ACCOUNT_BUTTON_BB, lambda: self.set_current_page(self.help)),
            Button(self.PAST_USER_ID_BUTTON_BB, lambda: self.set_current_page(None)),
            Button(self.PAST_PASSWORD_BUTTON_BB, lambda: self.set_current_page(self.account)),
            Button(self.PAST_URL_BUTTON_BB, lambda: self.set_current_page(self.help)),
            Button(self.PAST_NOTES_BUTTON_BB, lambda: self.set_current_page(None)),
        ]

    def set_hide_password(self, is_checked):
        "TODO"


    def render(self, img: np.ndarray):
        """ Renders the main window and all its children onto the given image.
        """
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.get_bb(), to_render)

        return img
    
    def ok(self):
        "TODO"

    def close(self):
        "TODO"

    def copy(self, fieldToCopy: str):
        "TODO"

    def past(self):
        "TODO"

    def handle_click(self, click_position: np.ndarray = None):
        pass

    @property
    def reward_template(self):
        return {
            "tire_20_setting": [False, True],
            "tire_22_setting": [False, True]
        }