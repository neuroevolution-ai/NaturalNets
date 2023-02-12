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
from naturalnets.environments.password_manager_app.reward_element import RewardElement
from naturalnets.environments.password_manager_app.utils import render_onto_bb
from naturalnets.environments.password_manager_app.widgets.button import Button
from naturalnets.environments.password_manager_app.widgets.check_box import CheckBox
from naturalnets.environments.password_manager_app.widgets.dropdown import Dropdown, DropdownItem


class AddAccount(Page, RewardElement):
    """todo"""

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "account_window/add_account_password_hide.png")

    BOUNDING_BOX = BoundingBox(0, 0, 448, 448)

    HIDE_PASSWORD_BB = BoundingBox(79, 209, 12, 13)

    OK_BUTTON_BB = BoundingBox(167, 415, 43, 20)
    CLOSE_BUTTON_BB = BoundingBox(219, 415, 62, 20)
    GENERATE_BUTTON_BB = BoundingBox(277, 178, 94, 19)
    LAUNCH_URL_BUTTON_BB = BoundingBox(349, 270, 23, 22)

    COPY_ACCOUNT_BUTTON_BB = BoundingBox(378, 33, 23, 22)
    COPY_USER_ID_BUTTON_BB = BoundingBox(378, 114, 23, 22)
    COPY_PASSWORD_BUTTON_BB = BoundingBox(378, 177, 23, 22)
    COPY_URL_BUTTON_BB = BoundingBox(378, 269, 23, 22)
    COPY_NOTES_BUTTON_BB = BoundingBox(378, 351, 23, 22)

    PAST_ACCOUNT_BUTTON_BB = BoundingBox(408, 33, 23, 22)
    PAST_USER_ID_BUTTON_BB = BoundingBox(408, 114, 23, 22)
    PAST_PASSWORD_BUTTON_BB = BoundingBox(408, 177, 23, 22)
    PAST_URL_BUTTON_BB = BoundingBox(408, 269, 23, 22)
    PAST_NOTES_BUTTON_BB = BoundingBox(408, 351, 23, 22)

    ACCOUNT_DD_BB = BoundingBox(77, 35, 296, 19)
    USER_ID_DD_BB = BoundingBox(77, 116, 296, 19)
    PASSWORD_DD_BB = BoundingBox(77, 179, 213, 19)
    URL_DD_BB = BoundingBox(77, 271, 265, 19)
    NOTES_DD_BB = BoundingBox(77, 350, 296, 24)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.name_one = DropdownItem(NAME_ONE, NAME_ONE)
        self.name_two = DropdownItem(NAME_TWO, NAME_TWO)
        self.name_three = DropdownItem(NAME_THREE, NAME_THREE)
        self.empty = DropdownItem(None, '')
        self.dropdown_account = Dropdown(self.ACCOUNT_DD_BB, [self.empty, self.name_one,
                                                   self.name_two,
                                                   self.name_three])

        self.dropdown_user_id = Dropdown(self.USER_ID_DD_BB, [self.empty, self.name_one,
                                                   self.name_two,
                                                   self.name_three])
        
        self.password_one = DropdownItem("1234", "1234")
        self.password_two = DropdownItem("qwer", "qwer")
        self.password_three = DropdownItem("asdf", "asdf")
        self.dropdown_password = Dropdown(self.PASSWORD_DD_BB, [self.password_one,
                                                   self.password_two,
                                                   self.password_three])
        
        self.current_password = self.random_password()
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
        self.opened_dd = None
        
        self.checkbox = CheckBox(
            self.HIDE_PASSWORD_BB,
            lambda is_checked: self.set_hide_password(is_checked)
        )
        self.checkbox.set_selected(1)
        self.add_widget(self.checkbox)

        self.buttons = [
            Button(self.OK_BUTTON_BB, lambda: self.ok()),
            Button(self.CLOSE_BUTTON_BB, lambda: self.cancel()),
            Button(self.GENERATE_BUTTON_BB, lambda: self.generate()),
            Button(self.COPY_ACCOUNT_BUTTON_BB, lambda: self.copy(self.dropdown_account)),
            Button(self.COPY_PASSWORD_BUTTON_BB, lambda: self.copy(self.dropdown_password)),
            Button(self.LAUNCH_URL_BUTTON_BB, lambda: self.launch_url()),
            Button(self.COPY_USER_ID_BUTTON_BB, lambda: self.copy(self.dropdown_user_id)),
            Button(self.COPY_URL_BUTTON_BB, lambda: self.copy(self.dropdown_url)),
            Button(self.COPY_NOTES_BUTTON_BB, lambda: self.copy(self.dropdown_notes)),
            Button(self.PAST_ACCOUNT_BUTTON_BB, lambda: self.past(self.dropdown_account)),
            Button(self.PAST_USER_ID_BUTTON_BB, lambda: self.past(self.dropdown_user_id)),
            Button(self.PAST_PASSWORD_BUTTON_BB, lambda: self.past(self.dropdown_password)),
            Button(self.PAST_URL_BUTTON_BB, lambda: self.past(self.dropdown_url)),
            Button(self.PAST_NOTES_BUTTON_BB, lambda: self.past(self.dropdown_notes)),
        ]

    def set_hide_password(self, is_checked: bool):
        self.is_checked = is_checked
        if is_checked:
            self.IMG_PATH = os.path.join(IMAGES_PATH, "account_window/add_account_password_hide.png")
            self.dropdown_password.set_selected_item(None)
        else:
            self.IMG_PATH = os.path.join(IMAGES_PATH, "account_window/add_account_empty_password_hide.png")
            self.dropdown_password.set_selected_item(self.current_password)
    
    def ok(self):
        
        account_name = self.dropdown_account.get_current_value()
        if account_name is not None:
            account_user_id = self.dropdown_user_id.get_current_value()  
            account_password = self.current_password.get_value()
            account_url = self.dropdown_url.get_current_value()
            account_notes = self.dropdown_notes.get_current_value()

            AccountManager.addAccount(Account(account_name, account_user_id, account_password, 
                                            account_url, account_notes))

        for dropdown in self.dropdowns:
            dropdown.set_selected_item(None)
            dropdown.close()

        self.opened_dd = None

        self.return_to_main_window()

    def cancel(self):
        for dropdown in self.dropdowns:
            dropdown.set_selected_item(None)
            dropdown.close()

        self.opened_dd = None

        self.return_to_main_window()

    def copy(self, dropdownToCopy: Dropdown):
        Cache.setCache(dropdownToCopy.get_current_value())

    def past(self, dropdownToPast: Dropdown):
        if Cache.getCache() is not None:
            dropdownToPast.set_selected_value(Cache.getCache())

    def generate(self):
        self.current_password = self.random_password()
        if not self.is_checked:
            self.dropdown_password.set_selected_item(self.current_password)

    def random_password(self):
        return random.choice(self.dropdown_password.get_all_items())

    def launch_url(self):
        pass


    def handle_click(self, click_position: np.ndarray = None):
        # Handle the case of an opened dropdown first
        if self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)
            if self.opened_dd == self.dropdown_password:
                self.current_password = self.dropdown_password.get_selected_item()
                if self.is_checked:
                    self.dropdown_password.set_selected_item(None)
            self.opened_dd = None
            return

        for button in self.buttons:
            if button.is_clicked_by(click_position):
                # check if figure printer button is visible
                button.handle_click(click_position)

        for dropdown in self.dropdowns:
            if dropdown.is_clicked_by(click_position):
                dropdown.handle_click(click_position)

                if dropdown.is_open():
                    self.opened_dd = dropdown
                return

        if self.checkbox.is_clicked_by(click_position):
            self.checkbox.handle_click(click_position)
    
    def reset(self):
        pass

    def return_to_main_window(self):
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.set_current_page(None)

    def render(self, img: np.ndarray):
        """ Renders the main window and all its children onto the given image.
        """
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.BOUNDING_BOX, to_render)
        for widget in self.get_widgets():
            img = widget.render(img)
        return img
    
    @property
    def reward_template(self):
        return {
            "tire_20_setting": [False, True],
            "tire_22_setting": [False, True]
        }