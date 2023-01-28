import os
import cv2
import numpy as np

from naturalnets.environments.gui_app.constants import IMAGES_PATH
from naturalnets.environments.password_manager_app.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.page import Page
from naturalnets.environments.password_manager_app.reward_element import RewardElement
from naturalnets.environments.password_manager_app.utils import render_onto_bb
from naturalnets.environments.password_manager_app.widgets.check_box import CheckBox
from naturalnets.environments.password_manager_app.widgets.dropdown import Dropdown, DropdownItem


class EditAccount(Page, RewardElement):
    """todo"""

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "")

    BOUNDING_BOX = BoundingBox(0, 0, 448, 448)

    HIDE_PASSWORD_BB = BoundingBox()

    OK_BUTTON_BB = BoundingBox()
    CLOSE_BUTTON_BB = BoundingBox()
    GENERATE_BUTTON_BB = BoundingBox()
    LAUNCH_URL_BUTTON_BB = BoundingBox()

    COPY_ACCOUNT_BUTTON_BB = BoundingBox()
    COPY_USER_ID_BUTTON_BB = BoundingBox()
    COPY_PASSWORD_BUTTON_BB = BoundingBox()
    COPY_URL_BUTTON_BB = BoundingBox()
    COPY_NOTES_BUTTON_BB = BoundingBox()

    PAST_ACCOUNT_BUTTON_BB = BoundingBox()
    PAST_USER_ID_BUTTON_BB = BoundingBox()
    PAST_PASSWORD_BUTTON_BB = BoundingBox()
    PAST_URL_BUTTON_BB = BoundingBox()
    PAST_NOTES_BUTTON_BB = BoundingBox()

    ACCOUNT_DD_BB = BoundingBox()
    USER_ID_DD_BB = BoundingBox()
    PASSWORD_DD_BB = BoundingBox()
    URL_DD_BB = BoundingBox()
    NOTES_DD_BB = BoundingBox()

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

    def set_hide_password(self, is_checked):
        "TODO"


    def render(self, img: np.ndarray):
        """ Renders the main window and all its children onto the given image.
        """
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.get_bb(), to_render)

        return img