"""The home window of the app, containing the menu as well as the respective pages"""
import logging
import os
from typing import Dict, List

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.widgets.button import Button, ShowPasswordButton
from naturalnets.environments.passlock_app.constants import (
    IMAGES_PATH, PAGES_SELECT_AREA_SIDE_BB, PAGES_SELECT_AREA_TOP_BB,
    PAGES_UI_AREA_BB, WINDOW_AREA_BB)
from naturalnets.environments.passlock_app.main_window_pages.auto_page import AutoPage
from naturalnets.environments.passlock_app.main_window_pages.manual_page import ManualPage
from naturalnets.environments.passlock_app.main_window_pages.search_page import SearchPage
from naturalnets.environments.passlock_app.main_window_pages.settings_page import SettingsPage

from naturalnets.environments.passlock_app.widgets.popup import PopUp



class HomeWindow(StateElement, Clickable, RewardElement):
    """The main window of the app, containing the menu as well as the respective pages
    (manual page, auto page, search page and setting page).

       State description:
            state[1]: represents the opened closed state of the home window.
            state[i]: represents the selected/shown status of page i, i in {0,..,3}.
    """

    STATE_LEN = 5
    IMG_PATH = os.path.join(IMAGES_PATH, "home_window.png")

    APP_BOUNDING_BOX = BoundingBox(0, 0, 1920, 1080)

    HOME_BUTTON_BB = BoundingBox(20, 150, 80, 80)
    SEARCH_BUTTON_BB = BoundingBox(20, 250, 80, 80)
    SETTINGS_BUTTON_BB = BoundingBox(20, 350, 80, 80)
    SYNC_BUTTON_BB = BoundingBox(20, 790, 80, 80)
    DARK_LIGHT_BB = BoundingBox(20, 890, 80, 80)

    MANUAL_BUTTON_BB = BoundingBox(140, 0, 155, 70)
    AUTO_BUTTON_BB = BoundingBox(295, 0, 150, 70)

    def __init__(self):
        StateElement.__init__(self, self.STATE_LEN)
        RewardElement.__init__(self)

        self._bounding_box = self.APP_BOUNDING_BOX

        self.manual = ManualPage()
        self.auto = AutoPage()
        self.search = SearchPage()
        self.settings = SettingsPage()

        self.pages: List[Page] = [self.manual,
                                  self.auto, self.search, self.settings]
        assert len(self.pages) == self.get_state_len() - 1

        self.current_page = None
        self.syncpopup = SyncPopUp()

        self.darkmode_button = ShowPasswordButton(self.DARK_LIGHT_BB, self.darkmode)

        self.buttons = [
            Button(self.HOME_BUTTON_BB,
                   lambda: self.set_current_page(self.manual)),
            Button(self.SEARCH_BUTTON_BB,
                   lambda: self.set_current_page(self.search)),
            Button(self.SETTINGS_BUTTON_BB,
                   lambda: self.set_current_page(self.settings)),
            Button(self.MANUAL_BUTTON_BB,
                   lambda: self.set_current_page(self.manual)),
            Button(self.AUTO_BUTTON_BB, lambda: self.set_current_page(self.auto)),
            self.darkmode_button,
            Button(self.SYNC_BUTTON_BB, self.syncpopup.open_popup)
        ]

        self.add_children([self.manual, self.auto, self.search, self.settings, self.syncpopup])
        self.set_reward_children(
            [self.manual, self.auto, self.search, self.settings, self.syncpopup])
        self.add_child(self.darkmode_button)
        self.pages_to_str: Dict[Page, str] = {
            self.manual: "manual",
            self.auto: "auto",
            self.search: "search",
            self.settings: "settings"
        }

    @property
    def reward_template(self):
        return {
            "home_window": ["open", "close"],
            "page_selected": ["manual", "auto", "search", "settings"],
            "darkmode_clicked": [True, False]
        }

    def reset(self):
        '''
        Resets the home window to its initial state.
        '''
        self.manual.reset()
        self.auto.reset()
        self.search.reset()
        self.settings.reset()
        self.current_page = None
        self.get_state()[:] = 0

    def close(self):
        """Closes the home window."""
        self.register_selected_reward(["home_window", "close"])

        self.get_state()[0] = 0

    def open(self):
        """Opens the home window."""
        self.register_selected_reward(["home_window", "open"])

        self.get_state()[0] = 1

    def is_open(self) -> int:
        """Returns if the settings window is open."""
        return self.get_state()[0]

    def get_current_page(self):
        '''Returns the currently selected/shown page.'''
        return self.current_page

    def set_current_page(self, page: Page):
        """Sets the currently selected/shown page, setting the respective
        state element to 1 and the state elements representing the other pages
        to 0.

        Args:
            page (Page): the page to be selected.
        """
        if self.current_page != page:
            self.get_state()[:] = 0
            self.get_state()[self.pages.index(page) + 1] = 1
            if not self.is_open():
                self.open()  # open the home window if it is closed

            page.reset()
            self.current_page = page

            # noinspection PyTypeChecker
            self.register_selected_reward(
                ["page_selected", self.pages_to_str[self.current_page]])

    def current_page_blocks_click(self) -> bool:
        """Returns true if the current page blocks clicks, i.e. has a dropdown/popup open.
        """
        return self.current_page.is_dropdown_open() or self.current_page.is_popup_open()

    def handle_click(self, click_position: np.ndarray) -> bool:
        """Handles a click on the home window.
        args:
            click_position (np.ndarray): the position of the click.
            returns: True if a login or signup was successful, False otherwise.
            """

        if self.is_popup_open():
            self.syncpopup.handle_click(click_position)
            return False

        #If the App is on the manual or auto page, the click is handled differently. In this case the top menu should also be clickable
        if self.current_page in (self.manual, self.auto):
            ##Pages UI Area is the area where the the page and not the menu is displayed
            if self.current_page_blocks_click() or PAGES_UI_AREA_BB.is_point_inside(click_position):
                return self.current_page.handle_click(click_position)

            # Check if side or top menu is clicked
            if (PAGES_SELECT_AREA_SIDE_BB.is_point_inside(click_position)
                    or PAGES_SELECT_AREA_TOP_BB.is_point_inside(click_position)):

                self.handle_menu_click(click_position)
                return False
        #In the other cases the click is handled normally and only the side menu is clickable
        else:
            # Check if the side menu is clicked
            if not self.current_page_blocks_click() and PAGES_SELECT_AREA_SIDE_BB.is_point_inside(click_position):
                self.handle_menu_click(click_position)
                return False

            ##Window Area is the area of the entire app
            if WINDOW_AREA_BB.is_point_inside(click_position):
                return self.current_page.handle_click(click_position)

    def handle_menu_click(self, click_position: np.ndarray) -> None:
        """Handles a click inside the menu bounding-box (performing the hit menu-button's action,
        if any).

        Args:
            click_position (np.ndarray): the click position (inside the menu-bounding-box).
        """
        for button in self.buttons:
            if button.is_clicked_by(click_position):

                button.handle_click(click_position)
                break

    def is_popup_open(self) -> bool:
        '''
        Returns True if a popup is open.
        '''
        return bool(self.syncpopup.is_open())

    def render(self, img: np.ndarray) -> np.ndarray:
        """
        Renders the main window and all its children onto the given image.
        returns: the rendered image.
        """

        if self.is_popup_open():
            img = self.syncpopup.render(img)
            return img

        img = self.current_page.render(img)

        return img

    def get_bb(self) -> BoundingBox:
        '''Returns the bounding box of the home window.'''
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox):
        '''Sets the bounding box of the home window.'''
        self._bounding_box = bounding_box

    def darkmode(self):
        '''
        Sets the home window to darkmode.
        '''
        self.register_selected_reward(["darkmode_clicked", self.darkmode_button.is_selected()])
        logging.debug("Darkmode not implemented yet")

    def sign_up(self):
        '''
        Signs up the user.
        '''
        self.set_current_page(self.manual)


class SyncPopUp(PopUp):
    """Popup for the calculator settings (pops up when no operator-checkbox is selected).

       State description:
            state[0]: the opened-state of this popup.
    """

    BOUNDING_BOX = BoundingBox(650, 340, 615, 325)
    IMG_PATH = os.path.join(
        IMAGES_PATH, "home_window_popup.png")

    def __init__(self):
        super().__init__(WINDOW_AREA_BB, self.BOUNDING_BOX, self.IMG_PATH)
        logging.debug("SettingsPageAboutPopUp created")
