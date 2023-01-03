from ast import List
import cv2
import numpy as np
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import get_group_bounding_box, render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.passlock_app.auth_window_pages.login_page import LoginPage
from naturalnets.environments.passlock_app.auth_window_pages.signup_page import SignupPage
from naturalnets.environments.passlock_app.main_window_pages.auto_page import AutoPage
from naturalnets.environments.passlock_app.main_window_pages.manual_page import ManualPage
from naturalnets.environments.passlock_app.main_window_pages.search_page import SearchPage
from naturalnets.environments.passlock_app.main_window_pages.settings_page import SettingsPage

class AuthenticationWindow(StateElement, Clickable, RewardElement):
    """The settings window ot the app, containing the different settings-pages, one for
    each page of the main-window pages.

       State description:
            state[0]: the opened-state of the settings window.
            state[i]: represents the selected/shown status of page i, i in {1,..,4}.
    """

    STATE_LEN = 3
    #IMG_PATH = os.path.join(IMAGES_PATH, "main_window_base.png")

    
    APP_BOUNDING_BOX = BoundingBox(0, 0, 1180, 850)

    EMAIL_TEXTFIELD_BB = BoundingBox(9, 56, 99, 22)
    PASSWORD_TEXTFIELD_BB = BoundingBox(9, 28, 99, 22)
    SHOW_PW_BUTTON_BB = BoundingBox(9, 112, 99, 22)
    SIGNUP_BUTTON_BB = BoundingBox(9, 84, 99, 22)
    LOGIN_BUTTON_BB = BoundingBox(9, 112, 99, 22)

    def __init__(self):
        StateElement.__init__(self, self.STATE_LEN)
        RewardElement.__init__(self)

        self.login = LoginPage()
        self.signup = SignupPage()

    
        self.pages: List[Page] = [self.login, self.signup]
        assert len(self.pages) == self.get_state_len() + 1

        self.current_page = None

        self.add_children([self.login, self.signup])
        self.set_reward_children([self.login, self.signup])    

        self.pages_to_str = {
            self.login: "login",
            self.signup: "signup",
        }
        
    
    @property
    def reward_template(self):
        return {
            "settings_window": ["open", "close"],
            "settings_tab_opened": [
                "text_printer_settings",
                "calculator_settings",
                "car_config_settings",
                "figure_printer_settings"
            ]
        }

    def reset(self):
        self.close()

        self.login.reset()
        self.signup.reset()
  
        self.set_current_tab(self.text_printer_settings)

    def is_open(self) -> int:
        """Returns if the settings window is open."""
        return self.get_state()[0]

    def open(self):
        """Opens the settings window."""
        self.register_selected_reward(["settings_window", "open"])

        self.get_state()[0] = 1

    def close(self):
        """Closes the settings window."""
        self.register_selected_reward(["settings_window", "close"])

        self.get_state()[0] = 0

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def handle_click(self, click_position: np.ndarray):
        # Check if current page is blocking click or click in current page bounding-box
        # (needs to be checked here since e.g. an opened dropdown should prevent a click
        # on the close button of the settings window)
        if (self.current_tab.is_popup_open()
                or self.current_tab.is_dropdown_open()
                or self.PAGE_BB.is_point_inside(click_position)):
            self.current_tab.handle_click(click_position)
            return

        # Check if close button clicked
        if self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
            return

        # Check if menu (tab-buttons) are clicked
        if self.tabs_bb.is_point_inside(click_position):
            self.handle_tabs_button_click(click_position)
            return

    def handle_tabs_button_click(self, click_position: np.ndarray) -> None:
        """Handles a click inside the menu bounding-box (performing the hit menu-button's action,
        if any).

        Args:
            click_position (np.ndarray): the click position (inside the menu-bounding-box).
        """
        for tab in self.tab_buttons:
            if tab.is_clicked_by(click_position):
                tab.handle_click(click_position)

    def set_current_tab(self, current_tab: Page):
        """Sets the currently selected/shown page/tab, setting the respective
        state element to 1 and the state elements representing the other pages/tabs
        to 0.

        Args:
            current_tab (Page): the page/tab to be selected.
        """
        for tab, index in self.tabs_to_state_index.items():
            if tab == current_tab:
                # If current_tab is None then this function is called on __init__ and we do not want
                # to give reward for this (i.e. change the reward dict)
                if self.current_tab is not None:
                    self.register_selected_reward(["settings_tab_opened", self.tabs_to_str[current_tab]])

                self.get_state()[index] = 1
                self.current_tab = current_tab
            else:
                self.get_state()[index] = 0

    def render(self, img: np.ndarray) -> np.ndarray:
        """ Renders the main window and all its children onto the given image.
        """
        to_render = cv2.imread(self.current_tab.get_img_path())
        
        img = render_onto_bb(img, self.get_bb(), to_render)
        self.current_tab.render(img)
        return img

    def get_tabs_bb(self, tab_buttons: List[Button]) -> BoundingBox:
        """Returns the bounding-box of the tabs-menu (bounding-box of all buttons)."""
        return get_group_bounding_box(tab_buttons)