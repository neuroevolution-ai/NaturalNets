import os

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button


class DowngradePopupPage(Page, RewardElement):
    
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(0, 0, 472, 147)
    IMG_PATH = os.path.join(IMAGES_PATH, "downgrade_popup.png")
    OK_BUTTON_BB = BoundingBox(366, 105, 91, 26)
    EXIT_BUTTON_BB = BoundingBox(430, 0, 42, 30)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DowngradePopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.ok_button: Button = Button(self.OK_BUTTON_BB, self.close())
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB, self.close())

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
        elif self.exit_button.is_clicked_by(click_position):
            self.exit_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]