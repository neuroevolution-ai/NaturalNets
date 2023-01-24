from typing import Dict, List
import os
import cv2

import numpy as np
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.passlock_app.constants import IMAGES_PATH, PAGES_SELECT_AREA_SIDE_BB, PAGES_SELECT_AREA_TOP_BB, PAGES_UI_AREA_BB, WINDOW_AREA_BB
from naturalnets.environments.passlock_app.main_window_pages.auto_page import AutoPage
from naturalnets.environments.passlock_app.main_window_pages.manual_page import ManualPage
from naturalnets.environments.passlock_app.main_window_pages.search_page import SearchPage
from naturalnets.environments.passlock_app.main_window_pages.settings_page import SettingsPage
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.passlock_app.utils import draw_rectangle_from_bb, draw_rectangles_around_clickables


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
    SYNC_BUTTON_BB = BoundingBox(9, 112, 99, 22)
    DARK_LIGHT_BB = BoundingBox(9, 112, 99, 22)

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

        self.is_darkmode = False
        self.change_mode_button = Button(
            self.DARK_LIGHT_BB,
            lambda: self.set_darkmode()
        )

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
            self.change_mode_button
        ]

        self.add_children([self.manual, self.auto, self.search, self.settings])
        self.set_reward_children(
            [self.manual, self.auto, self.search, self.settings])

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
            "page_selected": ["manual", "auto", "search", "settings"]
        }

    def reset(self):
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
            self.open()  # open the home window if it is closed

            #TODO reset the setings and search page after switching to another page so the popups are closed
            self.search.reset()
            self.settings.reset()
            self.current_page = page

            # noinspection PyTypeChecker
            self.register_selected_reward(
                ["page_selected", self.pages_to_str[self.current_page]])

    def current_page_blocks_click(self) -> bool:
        """Returns true if the current page blocks clicks, i.e. has a dropdown/popup open.
        """
        return self.current_page.is_dropdown_open() or self.current_page.is_popup_open()

    def handle_click(self, click_position: np.ndarray) -> None:
        # Let the current page process the click, if the current page blocks clicks
        # to the main page (e.g. due to open dropdowns) or the click
        # is inside the bounding box of the current page.
        # Note that the settings menu button is handled in the AppController class.

        if (self.current_page == self.manual or self.current_page == self.auto):
            if self.current_page_blocks_click() or PAGES_UI_AREA_BB.is_point_inside(click_position):
                self.current_page.handle_click(click_position)
                return

            # Check if menu is clicked
            if ((PAGES_SELECT_AREA_SIDE_BB.is_point_inside(click_position)
                    or PAGES_SELECT_AREA_TOP_BB.is_point_inside(click_position))):

                self.handle_menu_click(click_position)
                return
        else:

            if self.current_page_blocks_click() or WINDOW_AREA_BB.is_point_inside(click_position):
                if (self.current_page.handle_click(click_position)):
                    return True

            # Check if menu is clicked
            if ((PAGES_SELECT_AREA_SIDE_BB.is_point_inside(click_position))):
                self.handle_menu_click(click_position)
                return

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

    def render(self, img: np.ndarray):
        """ 
        Renders the main window and all its children onto the given image.
        """

        if (self.get_state()[1] == 1):
            img = self.manual.render(img)
        if (self.get_state()[2] == 1):
            img = self.auto.render(img)
        if (self.get_state()[3] == 1):
            img = self.search.render(img)
        if (self.get_state()[4] == 1):
            img = self.settings.render(img)

        # draw_rectangle_from_bb(img, PAGES_UI_AREA_BB, (0,255,0), 2)
        # draw_rectangles_around_clickables([self.buttons], img)
        return img

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def get_darkmode(self) -> bool:
        return self.is_darkmode
