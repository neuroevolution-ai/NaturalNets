import os

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button


class DeleteCheckPopupPage(Page,RewardElement):
    """
    STATE_LEN describes if the popup is open
    """
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(0, 0, 530, 135)
    IMG_PATH = os.path.join(IMAGES_PATH, "delete_check_popup.png")
    YES_BUTTON_BB = BoundingBox(335, 97, 87, 24)
    NO_BUTTON_BB = BoundingBox(430, 97, 87, 24)
    EXIT_BUTTON_BB = BoundingBox(491, 0, 39, 29)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeleteCheckPopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.yes_button: Button = Button(self.YES_BUTTON_BB,ProfileDatabase().delete_profile())
        self.no_button: Button = Button(self.NO_BUTTON_BB,self.close())
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB,self.close())

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }


    def handle_click(self, click_position: np.ndarray) -> None:
        if self.exit_button.is_clicked_by(click_position):
            self.exit_button.handle_click(click_position)
        elif self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
        elif self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]