import os
from typing import List, Union

import cv2
import numpy as np
from naturalnets.environments.password_manager_app.window_pages.account_window_pages.account_error import AccountError
from naturalnets.environments.password_manager_app.account_manager.account_manager import AccountManager

from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH, NAME_ONE, NAME_THREE, NAME_TWO
from naturalnets.environments.app_components.interfaces import Clickable
from naturalnets.environments.app_components.page import Page, Widget
from naturalnets.environments.app_components.state_element import StateElement
from naturalnets.environments.app_components.utils import render_onto_bb
from naturalnets.environments.app_components.widgets.button import Button
from naturalnets.environments.app_components.widgets.dropdown import Dropdown, DropdownItem
from naturalnets.environments.password_manager_app.window_pages.account_window_pages.add_account import AddAccount
from naturalnets.environments.password_manager_app.window_pages.account_window_pages.edit_account import EditAccount
from naturalnets.environments.password_manager_app.window_pages.account_window_pages.view_account import ViewAccount
from naturalnets.environments.password_manager_app.window_pages.account_window_pages.confirm_delete_account import (
    ConfirmDeleteAccount
)
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.account_bar import AccountBar
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.database import Database
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.help import Help
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.sub_window_pages.about import (
    About
)
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.sub_window_pages.file_system import (
    FileSystem
)
from naturalnets.environments.password_manager_app.window_pages.function_bar_window_pages.sub_window_pages.master_password import (
    MasterPassword
)
from naturalnets.environments.password_manager_app.window_pages.options import Options
from naturalnets.environments.password_manager_app.cache import Cache


class MainWindow(StateElement, Clickable):
    """The main page of the app, containing the main overview as well as all other pages.

    State description:
         _state[i]: represents the selected/shown status of page i, i in {0,..,11}.

         state_img[i][j]: represents the status of the main page. The combination of i in {0,..,7}
         and j in {0,..,3} represents the currently visible accounts as well as the currently selected
         account.
    """

    # Each state represents a page
    STATE_LEN = 15
    IMG_PATH = os.path.join(IMAGES_PATH, "main_window/main_window_0_accounts.png")

    # 1. Each state represents which specific accounts exists with a max. of 8 different states
    # 2. Represents which Account is selected
    STATE_IMG = [0, 0]

    BOUNDING_BOX = BoundingBox(0, 0, 448, 448)
    MENU_AREA_BB = BoundingBox(0, 3, 448, 133)

    ADD_ACCOUNT_BUTTON_BB = BoundingBox(2, 25, 30, 30)
    EDIT_ACCOUNT_BUTTON_BB = BoundingBox(33, 25, 30, 30)
    DELETE_ACCOUNT_BUTTON_BB = BoundingBox(64, 25, 30, 30)
    COPY_USERNAME_BUTTON_BB = BoundingBox(100, 25, 30, 30)
    COPY_PASSWORD_BUTTON_BB = BoundingBox(131, 25, 30, 30)
    LAUNCH_URL_BUTTON_BB = BoundingBox(162, 25, 30, 30)
    OPTIONS_BUTTON_BB = BoundingBox(199, 25, 30, 30)
    DATABASE_BB = BoundingBox(0, 4, 57, 19)
    ACCOUNT_BUTTON_BB = BoundingBox(58, 4, 53, 19)
    HELP_BUTTON_BB = BoundingBox(111, 4, 32, 19)
    RESET_SEARCH_BUTTON_BB = BoundingBox(149, 67, 15, 15)

    ACCOUNT_ONE_BB = BoundingBox(1, 90, 447, 14)
    ACCOUNT_TWO_BB = BoundingBox(1, 105, 447, 15)
    ACCOUNT_THREE_BB = BoundingBox(1, 121, 447, 14)

    SEARCH_DD_BB = BoundingBox(20, 65, 126, 20)

    def __init__(self):
        StateElement.__init__(self, self.STATE_LEN)

        self._bounding_box = self.BOUNDING_BOX
        self.current_page = None

        self.add_account = AddAccount()
        self.edit_account = EditAccount()
        self.view_account = ViewAccount()
        self.confirm_delete_account = ConfirmDeleteAccount()
        self.options = Options()
        self.database = Database()
        self.account_bar = AccountBar()
        self.help = Help()
        self.about = About()
        self.master_password = MasterPassword()
        self.file_system = FileSystem()
        self.account_error = AccountError()

        self.pages: List[Page] = [
            self.add_account,
            self.edit_account,
            self.options,
            self.database,
            self.account_bar,
            self.help,
            self.view_account,
            self.about,
            self.master_password,
            self.confirm_delete_account,
            self.file_system,
            self.account_error,
        ]
        assert len(self.pages) == self.get_state_len() - 3

        self.buttons = [
            Button(self.ADD_ACCOUNT_BUTTON_BB, lambda: self.function_add_account()),
            Button(self.EDIT_ACCOUNT_BUTTON_BB, lambda: self.function_edit_account()),
            Button(self.DELETE_ACCOUNT_BUTTON_BB, lambda: self.function_delete_account()),
            Button(self.COPY_USERNAME_BUTTON_BB, lambda: self.copy_username()),
            Button(self.COPY_PASSWORD_BUTTON_BB, lambda: self.copy_password()),
            Button(self.LAUNCH_URL_BUTTON_BB, lambda: self.launch_url()),
            Button(self.OPTIONS_BUTTON_BB, lambda: self.set_current_page(self.options)),
            Button(self.DATABASE_BB, lambda: self.set_current_page(self.database)),
            Button(self.ACCOUNT_BUTTON_BB, lambda: self.set_current_page(self.account_bar)),
            Button(self.HELP_BUTTON_BB, lambda: self.set_current_page(self.help)),
            Button(self.RESET_SEARCH_BUTTON_BB, lambda: self.reset_search()),
            Button(self.ACCOUNT_ONE_BB, lambda: self.handel_selection(1)),
            Button(self.ACCOUNT_TWO_BB, lambda: self.handel_selection(2)),
            Button(self.ACCOUNT_THREE_BB, lambda: self.handel_selection(3)),
        ]

        self.add_children(
            [
                self.add_account,
                self.edit_account,
                self.options,
                self.database,
                self.account_bar,
                self.help,
                self.view_account,
                self.about,
                self.master_password,
                self.confirm_delete_account,
                self.file_system,
                self.account_error,
            ]
        )

        self.widgets: List[Widget] = []

        self.name_one = DropdownItem(NAME_ONE, NAME_ONE)
        self.name_two = DropdownItem(NAME_TWO, NAME_TWO)
        self.name_three = DropdownItem(NAME_THREE, NAME_THREE)
        self.empty = DropdownItem(None, "")
        self.dropdown = Dropdown(self.SEARCH_DD_BB, [self.name_one, self.name_two, self.name_three])

        self.add_widget(self.dropdown)
        self.opened_dd = None
        self.search_active = False

    def reset(self):
        self.add_account.reset()
        self.edit_account.reset()
        self.view_account.reset()
        AccountManager.reset()

        self.set_current_page(None)
        self.refresh_state()
        self.refresh_image()

    def function_add_account(self) -> None:
        self.add_account.generate()
        self.set_current_page(self.add_account)

    def function_delete_account(self) -> None:
        account_to_delete = AccountManager.get_account_by_name(self.get_selected_account())
        if account_to_delete is not None:
            self.confirm_delete_account.set_name(self.get_selected_account())
            self.set_current_page(self.confirm_delete_account)

    def function_edit_account(self) -> None:
        account_to_edit = AccountManager.get_account_by_name(self.get_selected_account())
        if account_to_edit is not None:
            self.edit_account.set_account(account_to_edit)
            self.set_current_page(self.edit_account)

    def function_view_account(self) -> None:
        account_to_view = AccountManager.get_account_by_name(self.get_selected_account())
        if account_to_view is not None:
            self.view_account.set_account(account_to_view)
            self.set_current_page(self.view_account)

    def function_account_error(self, account_name: str) -> None:
        self.account_error.set_name(account_name)
        self.set_current_page(self.account_error)

    def copy_username(self) -> None:
        selected_account_name = self.get_selected_account()
        if selected_account_name is not None:
            selected_account = AccountManager.get_account_by_name(selected_account_name)
            if selected_account is not None:
                Cache.set_cache(selected_account.get_user_id())

    def copy_password(self) -> None:
        selected_account_name = self.get_selected_account()
        if selected_account_name is not None:
            selected_account = AccountManager.get_account_by_name(selected_account_name)
            if selected_account is not None:
                Cache.set_cache(selected_account.get_password())

    def launch_url(self) -> None:
        print("launch_url")

    def get_current_page(self) -> Union[Page, None]:
        return self.current_page

    def set_current_page(self, page: Page) -> None:
        """Sets the currently selected/shown page, setting the respective
        state element to 1 and the state elements representing the other pages
        to 0.

        Args:
            page (Page): the page to be selected.
        """
        if page is None:
            self.get_state()[:] = 0
            self.current_page = None
            self.refresh_state()
            if not self.search_active:
                self.refresh_image()

        elif self.current_page != page:
            self.get_state()[:] = 0
            self.get_state()[self.pages.index(page)] = 1
            self.current_page = page

    def current_page_blocks_click(self) -> bool:
        """Returns true if the current page blocks clicks, i.e. has a dropdown/popup open."""
        return self.current_page.is_dropdown_open() or self.current_page.is_popup_open()

    def handel_selection(self, selected: int) -> None:
        if self.STATE_IMG[0] < 4:
            return
        elif 3 < self.STATE_IMG[0] < 7:
            if selected < 3:
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
            # Check if a dropdown is open
            if self.opened_dd is not None:
                self.opened_dd.handle_click(click_position)
                self.search(self.dropdown.get_current_value())
                self.opened_dd = None
                return

            # Check if menu is clicked
            if self.MENU_AREA_BB.is_point_inside(click_position):
                self.handle_menu_click(click_position)
                return

    def handle_menu_click(self, click_position: np.ndarray) -> None:
        """Handles a click inside the menu bounding-box (performing the hit menu-button's action,
        if any).

        Args:
            click_position (np.ndarray): the click position (inside the menu-bounding-box).
        """
        for button in self.buttons:
            if self.search_active:
                if (
                    button.get_bb() == self.ACCOUNT_ONE_BB
                    or button.get_bb() == self.ACCOUNT_TWO_BB
                    or button.get_bb() == self.ACCOUNT_THREE_BB
                ):
                    break
                else:
                    if button.is_clicked_by(click_position):
                        # check if figure printer button is visible
                        button.handle_click(click_position)
            else:
                if button.is_clicked_by(click_position):
                    # check if figure printer button is visible
                    button.handle_click(click_position)

        if self.dropdown.is_clicked_by(click_position):
            self.dropdown.handle_click(click_position)

            if self.dropdown.is_open():
                self.opened_dd = self.dropdown

            return

    def render(self, img: np.ndarray):
        """Renders the main window and all its children onto the given image."""

        self
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.get_bb(), to_render)
        if self.current_page is not None:
            img = self.current_page.render(img)
        else:
            for widget in self.get_widgets():
                img = widget.render(img)
        return img

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def refresh_state(self) -> None:
        self.STATE_IMG = AccountManager.current_state()

        if self.STATE_IMG[0] == 0:
            self.get_state()[12] = 0
            self.get_state()[13] = 0
            self.get_state()[14] = 0
        elif self.STATE_IMG[0] == 1:
            self.get_state()[12] = 1
            self.get_state()[13] = 0
            self.get_state()[14] = 0
        elif self.STATE_IMG[0] == 2:
            self.get_state()[12] = 0
            self.get_state()[13] = 1
            self.get_state()[14] = 0
        elif self.STATE_IMG[0] == 3:
            self.get_state()[12] = 0
            self.get_state()[13] = 0
            self.get_state()[14] = 1
        elif self.STATE_IMG[0] == 4:
            self.get_state()[12] = 1
            self.get_state()[13] = 1
            self.get_state()[14] = 0
        elif self.STATE_IMG[0] == 5:
            self.get_state()[12] = 1
            self.get_state()[13] = 0
            self.get_state()[14] = 1
        elif self.STATE_IMG[0] == 6:
            self.get_state()[12] = 0
            self.get_state()[13] = 1
            self.get_state()[14] = 1
        elif self.STATE_IMG[0] == 7:
            self.get_state()[12] = 1
            self.get_state()[13] = 1
            self.get_state()[14] = 1

    def refresh_image(self) -> None:
        self.new_path = ""

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

        self.IMG_PATH = os.path.join(IMAGES_PATH, self.new_path)

    def get_selected_account(self) -> Union[str, None]:
        if self.search_active:
            if self.dropdown.get_current_value() == NAME_ONE:
                return NAME_ONE
            if self.dropdown.get_current_value() == NAME_TWO:
                return NAME_TWO
            if self.dropdown.get_current_value() == NAME_THREE:
                return NAME_THREE
            return None

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

    def search(self, account_name) -> None:
        if account_name is None:
            self.refresh_image()
            self.search_active = False
            return
        elif self.account_exists(account_name):
            if account_name == NAME_ONE:
                self.IMG_PATH = os.path.join(IMAGES_PATH, "main_window/main_window_Hanna_account.png")
                self.search_active = True

            elif account_name == NAME_TWO:
                self.IMG_PATH = os.path.join(IMAGES_PATH, "main_window/main_window_Klaus_account.png")
                self.search_active = True

            elif account_name == NAME_THREE:
                self.IMG_PATH = os.path.join(IMAGES_PATH, "main_window/main_window_Mariam_account.png")
                self.search_active = True
        else:
            self.IMG_PATH = os.path.join(IMAGES_PATH, "main_window/main_window_0_accounts.png")
            self.search_active = True

    def reset_search(self) -> None:
        self.dropdown.set_selected_item(self.empty)
        self.search_active = False
        self.refresh_image()

    def account_exists(self, account_name) -> bool:
        if account_name == NAME_ONE:
            if self.STATE_IMG[0] == 1 or self.STATE_IMG[0] == 4 or self.STATE_IMG[0] == 5 or self.STATE_IMG[0] == 7:
                return True
            else:
                return False

        elif account_name == NAME_TWO:
            if self.STATE_IMG[0] == 2 or self.STATE_IMG[0] == 4 or self.STATE_IMG[0] == 6 or self.STATE_IMG[0] == 7:
                return True
            else:
                return False

        elif account_name == NAME_THREE:
            if self.STATE_IMG[0] == 3 or self.STATE_IMG[0] == 5 or self.STATE_IMG[0] == 6 or self.STATE_IMG[0] == 7:
                return True
            else:
                return False

        return False

    def add_widget(self, widget: Widget) -> None:
        """Adds the given widget to this Page. This will also add the widget to the
        pages' StateElement-children."""
        self.widgets.append(widget)
        self.add_child(widget)

    def get_widgets(self) -> List[Widget]:
        """Returns all widgets of this page. Might differ from the pages' state-element children!"""
        return self.widgets
