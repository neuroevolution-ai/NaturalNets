import os
import numpy as np
from naturalnets.environments.password_manager_app.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH

from naturalnets.environments.password_manager_app.page import Page
from naturalnets.environments.password_manager_app.reward_element import RewardElement
from naturalnets.environments.password_manager_app.widgets.button import Button


class Account(Page, RewardElement):

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "function_bar/account.PNG")

    BOUNDING_BOX = BoundingBox(58, 4, 175, 179)
    MENU_AREA_BB = BoundingBox(58, 23, 175, 115)

    OPEN_DATABASE_BUTTON_BB = BoundingBox(0,0,1,1)
    Change_MASTER_PASSWORD_BUTTON_BB = BoundingBox(0,0,1,1)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.buttons = [
            Button(self.OPEN_DATABASE_BUTTON_BB, lambda: self.return_to_main_window()),
            Button(self.Change_MASTER_PASSWORD_BUTTON_BB, lambda: self.return_to_main_window()),
        ]

    def return_to_main_window(self):
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.set_current_page(None)

    def handle_click(self, click_position: np.ndarray = None):
        if self.MENU_AREA_BB.is_point_inside(click_position):
            self.handle_menu_click(click_position)
            return
        else:
            self.return_to_main_window()
        
    def handle_menu_click(self, click_position: np.ndarray = None):
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                # check if figure printer button is visible
                button.handle_click(click_position)

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