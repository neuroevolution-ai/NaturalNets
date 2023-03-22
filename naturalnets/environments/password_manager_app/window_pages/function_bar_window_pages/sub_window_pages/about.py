import os
import numpy as np
from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.password_manager_app.constants import IMAGES_PATH

from naturalnets.environments.app_components.page import Page
from naturalnets.environments.password_manager_app.page_manager import PageManager
from naturalnets.environments.app_components.widgets.button import Button


class About(Page):
    """A page with information about the application."""

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "function_bar/about.PNG")

    BOUNDING_BOX = BoundingBox(71, 111, 305, 198)

    OK_BUTTON_BB = BoundingBox(201, 276, 45, 21)
    CLOSE_BUTTON_BB = BoundingBox(346, 112, 30, 30)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)

        self.buttons = [
            Button(self.OK_BUTTON_BB, lambda: PageManager.return_to_main_page()),
            Button(self.CLOSE_BUTTON_BB, lambda: PageManager.return_to_main_page()),
        ]

    def handle_click(self, click_position: np.ndarray = None) -> None:
        for button in self.buttons:
            if button.is_clicked_by(click_position):
                # check if figure printer button is visible
                button.handle_click(click_position)

    def render(self, img: np.ndarray) -> np.ndarray:
        """Renders this page onto the given image."""
        return super().render(img)
