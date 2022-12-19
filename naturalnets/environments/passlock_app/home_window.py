from ast import List
import os
import cv2

import numpy as np
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.passlock_app.constants import IMAGES_PATH
from naturalnets.environments.passlock_app.main_window_pages.auto_page import AutoPage
from naturalnets.environments.passlock_app.main_window_pages.manual_page import ManualPage
from naturalnets.environments.passlock_app.main_window_pages.search_page import SearchPage
from naturalnets.environments.passlock_app.main_window_pages.settings_page import SettingsPage
from naturalnets.environments.gui_app.widgets.button import Button

class HomeWindow(StateElement, Clickable, RewardElement):
    """The main window of the app, containing the menu as well as the respective pages
    (manual page, auto page, search page and setting page).

       State description:
            state[i]: represents the selected/shown status of page i, i in {0,..,2}.
    """

    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "main_window_page.png")

    
    APP_BOUNDING_BOX = BoundingBox(0, 0, 1100, 850)

    HOME_BUTTON_BB = BoundingBox(9, 28, 99, 22)
    SEARCH_BUTTON_BB = BoundingBox(9, 56, 99, 22)
    SETTINGS_BUTTON_BB = BoundingBox(9, 84, 99, 22)
    SYNC_BUTTON_BB = BoundingBox(9, 112, 99, 22)
    DARK_LIGHT_BB = BoundingBox(9, 112, 99, 22)
    
    MANUAL_BUTTON_BB = BoundingBox(9, 28, 99, 22)
    AUTO_BUTTON_BB = BoundingBox(9, 28, 99, 22)

    PAGES_AREA_BB = BoundingBox(9, 28, 99, 22)
    MENU_AREA_BB = BoundingBox(9, 28, 99, 22)

    def __init__(self):
        StateElement.__init__(self, self.STATE_LEN)
        RewardElement.__init__(self)

        self._bounding_box = self.APP_BOUNDING_BOX

        self.manual = ManualPage()
        self.auto = AutoPage()
        self.search = SearchPage()
        self.settings = SettingsPage()

        self.pages: List[Page] = [self.manual, self.auto,self.search, self.settings]
        assert len(self.pages) == self.get_state_len()

        self.current_page = None

    
        self.is_darkmode = False
        self.change_mode_button = Button(
            self.DARK_LIGHT_BB,
            lambda: self.set_current_page(self.manual)
        )

        self.buttons = [
            Button(self.HOME_BUTTON_BB, lambda: self.set_current_page(self.manual)),
            Button(self.SEARCH_BUTTON_BB, lambda: self.set_current_page(self.search)),
            Button(self.SETTINGS_BUTTON_BB, lambda: self.set_current_page(self.settings)),
            Button(self.MANUAL_BUTTON_BB, lambda: self.set_current_page(self.manual)),
            Button(self.AUTO_BUTTON_BB, lambda: self.set_current_page(self.auto)),
            self.change_mode_button
        ]
        

        self.add_children([self.manual, self.auto, self.search, self.settings])
        self.set_reward_children([self.manual, self.auto, self.search, self.settings])

        self.pages_to_str = {
            self.manual: "manual",
            self.auto: "auto",
            self.search: "search",
            self.settings: "settings"
        }
    
    @property
    def reward_template(self):
        return {
            "page_selected": ["manual", "auto", "search", "settings"]
        }
    
    def reset(self):
        self.manual.reset()
        self.auto.reset()
        self.search.reset()
        self.settings.reset()

        self.is_password_visible = 0
        self.is_darkmode = 0
        self.set_current_page(self.manual)

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
            self.get_state()[self.pages.index(page)] = 1
            self.current_page = page

            # noinspection PyTypeChecker
            self.register_selected_reward(["page_selected", self.pages_to_str[self.current_page]])

    def current_page_blocks_click(self) -> bool:
        """Returns true if the current page blocks clicks, i.e. has a dropdown/popup open.
        """
        return self.current_page.is_dropdown_open() or self.current_page.is_popup_open() 

    def handle_click(self, click_position: np.ndarray) -> None:
        # Let the current page process the click, if the current page blocks clicks
        # to the main page (e.g. due to open dropdowns) or the click
        # is inside the bounding box of the current page.
        # Note that the settings menu button is handled in the AppController class.
        if self.current_page_blocks_click() or self.PAGES_AREA_BB.is_point_inside(click_position):
            self.current_page.handle_click(click_position)
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
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)
                break  

    def render(self, img: np.ndarray):
        """ Renders the main window and all its children onto the given image.
        """
        to_render = cv2.imread(self.IMG_PATH)
        img = render_onto_bb(img, self.get_bb(), to_render)
        img = self.current_page.render(img)

        if self.is_darkmode:
            figure_printer_img = cv2.imread(self.FIGURE_PRINTER_BUTTON_IMG_PATH)
            img = render_onto_bb(img, self.FIGURE_PRINTER_BUTTON_BB, figure_printer_img)

        return img

    def get_bb(self) -> BoundingBox:
                                                                                                                                                                                                                                               
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box
