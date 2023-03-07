import os
import numpy as np
from naturalnets.environments.password_manager_app.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH

from naturalnets.environments.password_manager_app.page import Page
from naturalnets.environments.password_manager_app.reward_element import RewardElement
from naturalnets.environments.password_manager_app.widgets.button import Button
from naturalnets.environments.password_manager_app.widgets.dropdown import Dropdown, DropdownItem


class MasterPassword(Page, RewardElement):

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "function_bar/master_password.PNG")

    BOUNDING_BOX = BoundingBox(57, 147, 334, 127)

    OK_BUTTON_BB = BoundingBox(143, 237, 57, 23)
    ABORT_BUTTON_BB = BoundingBox(229, 237, 57, 23)

    PASSWORD_DD_BB = BoundingBox(115, 207, 265, 20)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.buttons = [
            Button(self.OK_BUTTON_BB, lambda: self.return_to_main_window()),
            Button(self.ABORT_BUTTON_BB, lambda: self.return_to_main_window()),
        ]

        self.password_one = DropdownItem("1234", "1234")
        self.password_two = DropdownItem("qwer", "qwer")
        self.password_three = DropdownItem("asdf", "asdf")
        self.dropdown = Dropdown(self.PASSWORD_DD_BB, [self.password_one,
                                                   self.password_two,
                                                   self.password_three])
        
        self.add_widget(self.dropdown)
        self.opened_dd = None

    def return_to_main_window(self):
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.set_current_page(None)

        self.dropdown.set_selected_item(None)
        self.dropdown.close()
        self.opened_dd = None

    def handle_click(self, click_position: np.ndarray = None):
        if self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)
            self.opened_dd = None
            return

        for button in self.buttons:
            if button.is_clicked_by(click_position):
                # check if figure printer button is visible
                button.handle_click(click_position)

        if self.dropdown.is_clicked_by(click_position):
            self.dropdown.handle_click(click_position)

            if self.dropdown.is_open():
                self.opened_dd = self.dropdown
            return

    def render(self, img: np.ndarray):
        """ Renders the main window and all its children onto the given image.
        """
        return super().render(img)
    
    @property
    def reward_template(self):
        return {
            "tire_20_setting": [False, True],
            "tire_22_setting": [False, True]
        }
