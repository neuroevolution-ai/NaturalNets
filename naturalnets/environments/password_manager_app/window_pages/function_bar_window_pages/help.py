import os
import numpy as np
from naturalnets.environments.password_manager_app.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH

from naturalnets.environments.password_manager_app.page import Page
from naturalnets.environments.password_manager_app.page_manager import PageManager
from naturalnets.environments.password_manager_app.widgets.button import Button


class Help(Page):
    """ The menu for help on the function bar. """

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "function_bar/help.PNG")

    BOUNDING_BOX = BoundingBox(110, 4, 84, 47)
    MENU_AREA_BB = BoundingBox(110, 23, 84, 28)

    ABOUT_BUTTON_BB = BoundingBox(112, 25, 80, 22)


    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)

        self.buttons = [
            Button(self.ABOUT_BUTTON_BB, lambda: PageManager.open_about()),
        ]

    def handle_click(self, click_position: np.ndarray = None) -> None:
        if self.MENU_AREA_BB.is_point_inside(click_position):
            self.handle_menu_click(click_position)
            return
        else:
            PageManager.return_to_main_window().return_to_main_window()
        
    def handle_menu_click(self, click_position: np.ndarray = None) -> None:
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)

    def render(self, img: np.ndarray) -> np.ndarray:
        """ Renders this page onto the given image.
        """
        return super().render(img)
