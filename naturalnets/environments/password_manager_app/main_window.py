import os
from typing import List

import cv2
import numpy as np
from naturalnets.environments.password_manager_app.account_manager.account_manager import AccountManager

from naturalnets.environments.password_manager_app.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH, NAME_ONE, NAME_THREE, NAME_TWO
from naturalnets.environments.password_manager_app.interfaces import Clickable
from naturalnets.environments.password_manager_app.page import Page
from naturalnets.environments.password_manager_app.reward_element import RewardElement
from naturalnets.environments.password_manager_app.state_element import StateElement
from naturalnets.environments.password_manager_app.utils import render_onto_bb
from naturalnets.environments.password_manager_app.widgets.button import Button
from naturalnets.environments.password_manager_app.window_pages.account_window_pages.add_account import AddAccount
from naturalnets.environments.password_manager_app.window_pages.account_window_pages.edit_account import EditAccount
from naturalnets.environments.password_manager_app.window_pages.account_window_pages.view_account import ViewAccount
from naturalnets.environments.password_manager_app.window_pages.account_window_pages.confirm_delete_account import ConfirmDeleteAccount
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.account import Account
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.database import Database
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.help import Help
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.sub_window_pages.about import About
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.sub_window_pages.invalid_url import InvalidURL
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.sub_window_pages.master_password import MasterPassword
from naturalnets.environments.password_manager_app.window_pages.options import Options


class MainWindow(StateElement, Clickable, RewardElement):
    """The main window of the app, containing the menu as well as the respective pages
    (text printer, calculator, car configurator and figure printer).

       State description:
            state[i]: represents the selected/shown status of page i, i in {0,..,3}.
    """

    # Each state represents the number of accounts that exists (with a max. of 3)
    STATE_LEN = 11
    IMG_PATH = os.path.join(IMAGES_PATH, "main_window/main_window_0_accounts.png")

    # 1. Each state represents which specific accounts exists with a max. of 8 different states 
    # 2. Represents which Account is selected
    STATE_IMG = [0, 0]

    BOUNDING_BOX = BoundingBox(0, 0, 448, 448)
    MENU_AREA_BB = BoundingBox(0, 24, 448, 112) #TODO

    ADD_ACCOUNT_BUTTON_BB = BoundingBox(2, 25, 30, 30)
    EDIT_ACCOUNT_BUTTON_BB = BoundingBox(33, 25, 30, 30)
    DELETE_ACCOUNT_BUTTON_BB = BoundingBox(64, 25, 30, 30)
    COPY_USERNAME_BUTTON_BB = BoundingBox(100, 25, 30, 30)
    COPY_PASSWORD_BUTTON_BB = BoundingBox(131, 25, 30, 30)
    LAUNCH_URL_BUTTON_BB = BoundingBox(162, 25, 30, 30)
    OPTIONS_BUTTON_BB = BoundingBox(199, 25, 30, 30)
    DATABASE_BB = BoundingBox(0, 0, 1, 1)
    ACCOUNT_BUTTON_BB = BoundingBox(0, 0, 1, 1)
    HELP_BUTTON_BB = BoundingBox(0, 0, 1, 1)
    RESET_SEARCH_BUTTON_BB = BoundingBox(0, 0, 1, 1)

    ACCOUNT_ONE_BB = BoundingBox(1, 90, 447, 14)
    ACCOUNT_TWO_BB = BoundingBox(1, 105, 447, 15)
    ACCOUNT_THREE_BB = BoundingBox(1, 121, 447, 14)

    SEARCH_DD_BB = BoundingBox(0,0,0,0)

    def __init__(self):
        StateElement.__init__(self, self.STATE_LEN)
        RewardElement.__init__(self)

        self._bounding_box = self.BOUNDING_BOX
        self.current_page = None

        self.add_account = AddAccount()
        self.edit_account = EditAccount()
        self.view_account = ViewAccount()
        self.confirm_delete_account = ConfirmDeleteAccount()
        self.options = Options()
        self.database = Database()
        self.account = Account()
        self.help = Help()
        self.about = About()
        self.invalid_url = InvalidURL()
        self.master_password = MasterPassword()

        self.pages: List[Page] = [self.add_account, self.edit_account,
                                  self.options, self.database,
                                  self.account, self.help,
                                  self.view_account, self.about,
                                  self.invalid_url, self.master_password,
                                  self.confirm_delete_account]
        # assert len(self.pages) == self.get_state_len()

        self.buttons = [
            Button(self.ADD_ACCOUNT_BUTTON_BB, lambda: self.function_add_account()),
            Button(self.EDIT_ACCOUNT_BUTTON_BB, lambda: self.function_edit_account()),
            Button(self.DELETE_ACCOUNT_BUTTON_BB, lambda: self.delete_account()),
            Button(self.COPY_USERNAME_BUTTON_BB, lambda: self.copy_username()),
            Button(self.COPY_PASSWORD_BUTTON_BB, lambda: self.copy_password()),
            Button(self.LAUNCH_URL_BUTTON_BB, lambda: self.launch_url()),
            Button(self.OPTIONS_BUTTON_BB, lambda: self.set_current_page(self.options)),
            Button(self.DATABASE_BB, lambda: self.set_current_page(self.database)),
            Button(self.ACCOUNT_BUTTON_BB, lambda: self.set_current_page(self.account)),
            Button(self.HELP_BUTTON_BB, lambda: self.set_current_page(self.help)),
            Button(self.RESET_SEARCH_BUTTON_BB, lambda: self.set_current_page(None)),
            Button(self.ACCOUNT_ONE_BB, lambda: self.handel_selection(1)),
            Button(self.ACCOUNT_TWO_BB, lambda: self.handel_selection(2)),
            Button(self.ACCOUNT_THREE_BB, lambda: self.handel_selection(3)),
        ]

        self.add_children([self.add_account, self.edit_account,
                                self.options, self.database,
                                self.account, self.help,
                                self.view_account, self.about,
                                self.invalid_url, self.master_password, 
                                self.confirm_delete_account])
        self.set_reward_children([self.add_account, self.edit_account,
                                self.options, self.database,
                                self.account, self.help,
                                self.view_account, self.about,
                                self.invalid_url, self.master_password,
                                self.confirm_delete_account])

        self.pages_to_str = {
            None: "None",
            self.add_account: "add_account",
            self.edit_account: "edit_account",
            self.options: "options",
            self.database: "database",
            self.account: "account",
            self.help: "help",
            self.view_account: "view_account",
            self.about: "about",
            self.invalid_url: "invalid_url",
            self.master_password: "master_password",
            self.confirm_delete_account: "confirm_delete_account"
        }

    @property
    def reward_template(self):
        return {
            "page_selected": ["add_account", "edit_account", "options", "account", "help", "view_account", "about", "invalid_url", "master_password", "confirm_delete_account", "None"]
        }

    def reset(self):
        # self.add_account.reset()
        # self.edit_account.reset()
        # self.options.reset()
        # self.database.reset()
        # self.account.reset()
        # self.help.reset()
        # self.view_account.reset()
        # self.about.reset()
        # self.invalid_url.reset()
        # self.master_password.reset()
        # self.confirm_delete_account.reset()

        self.set_current_page(None)

    def function_add_account(self):
        self.add_account.generate()
        self.set_current_page(self.add_account)

    def delete_account(self):
        if 0 < self.STATE_IMG[1] < 4:
            self.confirm_delete_account.set_name(self.get_selected_account())
            self.set_current_page(self.confirm_delete_account)
    
    def function_edit_account(self):
        if 0 < self.STATE_IMG[1] < 4:
            account_to_edit = AccountManager.getAccountByName(self.get_selected_account())
            if account_to_edit is not None:
                self.edit_account.set_account(account_to_edit)
                self.set_current_page(self.edit_account)

    def copy_username(self):
        print('copy_username')

    def copy_password(self):
        print('copy_password')

    def launch_url(self):
        print('launch_url')

    def get_current_page(self):
        return self.current_page

    def set_current_page(self, page: Page):
        """Sets the currently selected/shown page, setting the respective
        state element to 1 and the state elements representing the other pages
        to 0.

        Args:
            page (Page): the page to be selected.
        """
        if page == None:
            self.get_state()[:] = 0
            self.current_page = None
            self.refresh_state()
            self.refresh_image()

            # noinspection PyTypeChecker
            self.register_selected_reward(["page_selected", self.pages_to_str[self.current_page]])

        elif self.current_page != page:
            self.get_state()[:] = 0
            self.get_state()[self.pages.index(page)] = 1
            self.current_page = page

            # noinspection PyTypeChecker
            self.register_selected_reward(["page_selected", self.pages_to_str[self.current_page]])

    def current_page_blocks_click(self) -> bool:
        """Returns true if the current page blocks clicks, i.e. has a dropdown/popup open.
        """
        return self.current_page.is_dropdown_open() or self.current_page.is_popup_open()
    
    def handel_selection(self, selected: int):
        print('enter selection')
        print(selected)
        if self.STATE_IMG[0] < 4:
            return
        elif 3 < self.STATE_IMG[0] < 7:
            if selected < 3:
                print('newSelection')
                self.STATE_IMG[1] = selected
                self.refresh_image() 
        elif self.STATE_IMG[0] == 7:
            self.STATE_IMG[1] = selected
            self.refresh_image() 

    def handle_click(self, click_position: np.ndarray) -> None:
        # Let the current page process the click, if the current page blocks clicks
        # to the main page (e.g. due to open dropdowns) or the click
        # is inside the bounding box of the current page.
        if self.current_page is not None:
            self.current_page.handle_click(click_position)
            return
        else:
            # Check if menu is clicked
            if self.MENU_AREA_BB.is_point_inside(click_position):
                self.handle_menu_click(click_position)
                return

    def is_dropdown_open(self):
        """Returns true if the current page has an opened dropdown.
        """
        if self.current_page is not None:
            return self.current_page.is_dropdown_open()
        else :
            return False

    def handle_menu_click(self, click_position: np.ndarray) -> None:
        """Handles a click inside the menu bounding-box (performing the hit menu-button's action,
        if any).

        Args:
            click_position (np.ndarray): the click position (inside the menu-bounding-box).
        """
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                # check if figure printer button is visible
                button.handle_click(click_position)

    def render(self, img: np.ndarray):
        """ Renders the main window and all its children onto the given image.
        """
        
        self
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if (self.current_page is not None):
            img = self.current_page.render(img)

        return img

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def refresh_state(self):
        self.STATE_IMG = AccountManager.current_state()

    def refresh_image(self):
        self.new_path = ''

        if self.STATE_IMG[0] == 0:
            self.new_path = "main_window/main_window_0_accounts.png"
        elif self.STATE_IMG[0] == 1:
                self.new_path = "main_window/main_window_Hanna_account.png"
        elif self.STATE_IMG[0] == 2:
                self.new_path = "main_window/main_window_Klaus_account.png"
        elif self.STATE_IMG[0] == 3:
                self.new_path = "main_window/main_window_Mariam_account.png"
        elif self.STATE_IMG[0] == 4:
            if self.STATE_IMG[1] == 0:
                self.new_path = "main_window/main_window_2_accounts_H_K.png"
            elif self.STATE_IMG[1] == 1:
                self.new_path = "main_window/main_window_2_accounts_H_selected_K.png"
            elif self.STATE_IMG[1] == 2:
                self.new_path = "main_window/main_window_2_accounts_H_K_selected.png"
        elif self.STATE_IMG[0] == 5:
            if self.STATE_IMG[1] == 0:
                self.new_path = "main_window/main_window_2_accounts_H_M.png"
            elif self.STATE_IMG[1] == 1:
                self.new_path = "main_window/main_window_2_accounts_H_selected_M.png"
            elif self.STATE_IMG[1] == 2:
                self.new_path = "main_window/main_window_2_accounts_H_M_selected.png"
        elif self.STATE_IMG[0] == 6:
            if self.STATE_IMG[1] == 0:
                self.new_path = "main_window/main_window_2_accounts_K_M.png"
            elif self.STATE_IMG[1] == 1:
                self.new_path = "main_window/main_window_2_accounts_K_selected_M.png"
            elif self.STATE_IMG[1] == 2:
                self.new_path = "main_window/main_window_2_accounts_K_M_selected.png"
        elif self.STATE_IMG[0] == 7:
            if self.STATE_IMG[1] == 0:
                self.new_path = "main_window/main_window_3_accounts.png"
            elif self.STATE_IMG[1] == 1:
                self.new_path = "main_window/main_window_3_accounts_H_selected.png"
            elif self.STATE_IMG[1] == 2:
                self.new_path = "main_window/main_window_3_accounts_K_selected.png"
            elif self.STATE_IMG[1] == 3:
                self.new_path = "main_window/main_window_3_accounts_M_selected.png"
            
        print('PAth set to:' + self.new_path)
        self.IMG_PATH = os.path.join(IMAGES_PATH, self.new_path)

    def get_selected_account(self):
        if self.STATE_IMG[0] == 0:
            return None
        elif self.STATE_IMG[0] == 1:
                return NAME_ONE
        elif self.STATE_IMG[0] == 2:
                return NAME_TWO
        elif self.STATE_IMG[0] == 3:
                return NAME_THREE
        elif self.STATE_IMG[0] == 4:
            if self.STATE_IMG[1] == 0:
                return None
            elif self.STATE_IMG[1] == 1:
                return NAME_ONE
            elif self.STATE_IMG[1] == 2:
                return NAME_TWO
        elif self.STATE_IMG[0] == 5:
            if self.STATE_IMG[1] == 0:
                return None
            elif self.STATE_IMG[1] == 1:
                return NAME_ONE
            elif self.STATE_IMG[1] == 2:
                return NAME_THREE
        elif self.STATE_IMG[0] == 6:
            if self.STATE_IMG[1] == 0:
                return None
            elif self.STATE_IMG[1] == 1:
                return NAME_TWO
            elif self.STATE_IMG[1] == 2:
                return NAME_THREE
        elif self.STATE_IMG[0] == 7:
            if self.STATE_IMG[1] == 0:
                return None
            elif self.STATE_IMG[1] == 1:
                return NAME_ONE
            elif self.STATE_IMG[1] == 2:
                return NAME_TWO
            elif self.STATE_IMG[1] == 3:
                return NAME_THREE

