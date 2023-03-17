import os
import cv2
import numpy as np
import random
from naturalnets.environments.password_manager_app.account_manager.account import Account
from naturalnets.environments.password_manager_app.account_manager.account_manager import AccountManager
from naturalnets.environments.password_manager_app.cache import Cache

from naturalnets.environments.password_manager_app.constants import IMAGES_PATH, NAME_ONE, NAME_THREE, NAME_TWO
from naturalnets.environments.password_manager_app.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.page import Page
from naturalnets.environments.password_manager_app.page_manager import PageManager
from naturalnets.environments.password_manager_app.utils import render_onto_bb
from naturalnets.environments.password_manager_app.widgets.button import Button
from naturalnets.environments.password_manager_app.widgets.check_box import CheckBox
from naturalnets.environments.password_manager_app.widgets.dropdown import Dropdown, DropdownItem


class ViewAccount(Page):
    """ This page gives a representation of an existing account. """

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "account_window/view_account_hide.png")

    BOUNDING_BOX = BoundingBox(0, 0, 448, 448)

    HIDE_PASSWORD_BB = BoundingBox(79, 209, 12, 13)

    OK_BUTTON_BB = BoundingBox(201, 414, 45, 21)

    LAUNCH_URL_BUTTON_BB = BoundingBox(349, 270, 23, 22)

    COPY_ACCOUNT_BUTTON_BB = BoundingBox(378, 33, 23, 22)
    COPY_USER_ID_BUTTON_BB = BoundingBox(378, 114, 23, 22)
    COPY_PASSWORD_BUTTON_BB = BoundingBox(378, 177, 23, 22)
    COPY_URL_BUTTON_BB = BoundingBox(378, 269, 23, 22)
    COPY_NOTES_BUTTON_BB = BoundingBox(378, 351, 23, 22)

    ACCOUNT_DD_BB = BoundingBox(77, 35, 296, 19)
    USER_ID_DD_BB = BoundingBox(77, 116, 296, 19)
    PASSWORD_DD_BB = BoundingBox(77, 179, 213, 19)
    URL_DD_BB = BoundingBox(77, 271, 265, 19)
    NOTES_DD_BB = BoundingBox(77, 350, 296, 24)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)

        self.account_to_edit = None

        self.name_one = DropdownItem(NAME_ONE, NAME_ONE)
        self.name_two = DropdownItem(NAME_TWO, NAME_TWO)
        self.name_three = DropdownItem(NAME_THREE, NAME_THREE)
        self.empty = DropdownItem(None, '')
        self.names = [self.empty, self.name_one, self.name_two, self.name_three]

        self.dropdown_account = Dropdown(self.ACCOUNT_DD_BB, [self.empty, self.name_one,
                                                   self.name_two,
                                                   self.name_three])

        self.dropdown_user_id = Dropdown(self.USER_ID_DD_BB, [self.empty, self.name_one,
                                                   self.name_two,
                                                   self.name_three])
        
        self.password_one = DropdownItem("1234", "1234")
        self.password_two = DropdownItem("qwer", "qwer")
        self.password_three = DropdownItem("asdf", "asdf")
        self.passwords = [self.password_one, self.password_two, self.password_three]

        self.dropdown_password = Dropdown(self.PASSWORD_DD_BB, [self.password_one,
                                                   self.password_two,
                                                   self.password_three])
        
        self.current_password = self.empty
        self.is_checked = True

        self.dropdown_url = Dropdown(self.URL_DD_BB, [self.empty, self.name_one,
                                                   self.name_two,
                                                   self.name_three])

        self.dropdown_notes = Dropdown(self.NOTES_DD_BB, [self.empty, self.name_one,
                                                   self.name_two,
                                                   self.name_three])
    
        self.dropdowns = [self.dropdown_account,
                          self.dropdown_user_id,
                          self.dropdown_password,
                          self.dropdown_url,
                          self.dropdown_notes]
        
        self.add_widgets(self.dropdowns)

        for dropdown in self.dropdowns:
            dropdown.set_clickable(False)
        
        self.checkbox = CheckBox(
            self.HIDE_PASSWORD_BB,
            lambda is_checked: self.set_hide_password(is_checked)
        )
        self.checkbox.set_selected(1)
        self.add_widget(self.checkbox)

        self.buttons = [
            Button(self.OK_BUTTON_BB, lambda: self.ok()),
            Button(self.COPY_ACCOUNT_BUTTON_BB, lambda: self.copy(self.dropdown_account)),
            Button(self.COPY_PASSWORD_BUTTON_BB, lambda: self.copy(self.dropdown_password)),
            Button(self.LAUNCH_URL_BUTTON_BB, lambda: self.launch_url()),
            Button(self.COPY_USER_ID_BUTTON_BB, lambda: self.copy(self.dropdown_user_id)),
            Button(self.COPY_URL_BUTTON_BB, lambda: self.copy(self.dropdown_url)),
            Button(self.COPY_NOTES_BUTTON_BB, lambda: self.copy(self.dropdown_notes)),
        ]

    def set_hide_password(self, is_checked: bool) -> None:
        self.is_checked = is_checked
        if is_checked:
            self.IMG_PATH = os.path.join(IMAGES_PATH, "account_window/view_account_hide.png")
            self.dropdown_password.set_selected_item(None)
        else:
            self.IMG_PATH = os.path.join(IMAGES_PATH, "account_window/view_account_not_hide.png")
            self.dropdown_password.set_selected_item(self.current_password)
    
    def ok(self) -> None:
        self.reset()
        PageManager.return_to_main_page()

    def copy(self, dropdownToCopy: Dropdown) -> None:
        Cache.set_cache(dropdownToCopy.get_current_value())

    def past(self, dropdownToPast: Dropdown) -> None:
        dropdownToPast.set_selected_value(Cache.get_cache())

    def launch_url(self) -> None:
        pass

    def set_account(self, account: Account) -> None:
        self.account_to_edit = account
        self.load_account()
    
    def load_account(self) -> None:
        self.dropdown_account.set_selected_value(self.account_to_edit.get_account_name())
        self.dropdown_user_id.set_selected_value(self.account_to_edit.get_user_id())
        self.dropdown_url.set_selected_value(self.account_to_edit.get_url())
        self.dropdown_notes.set_selected_value(self.account_to_edit.get_notes())

        new_password = self.account_to_edit.get_password()

        for password in self.passwords:
            if new_password == password.get_value():
                self.current_password = password

    def handle_click(self, click_position: np.ndarray = None) -> None:
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)

        if self.checkbox.is_clicked_by(click_position):
            self.checkbox.handle_click(click_position)
    
    def reset(self) -> None:
        for dropdown in self.dropdowns:
            dropdown.set_selected_item(None)
            dropdown.close()

        self.checkbox.set_selected(1)
        self.set_hide_password(True)


    def render(self, img: np.ndarray) -> np.ndarray:
        """ Renders this page onto the given image.
        """
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.BOUNDING_BOX, to_render)
        for widget in self.get_widgets():
            img = widget.render(img)
        return img
    