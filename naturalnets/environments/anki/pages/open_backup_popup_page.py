import os

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class OpenBackupPopup(Page, RewardElement):

    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(0, 0, 400, 146)
    IMG_PATH = os.path.join(IMAGES_PATH,"open_backup_popup.png")
    YES_BUTTON_BB = BoundingBox(194, 106, 90, 26)
    NO_BUTTON_BB = BoundingBox(296, 106, 90, 26)
    EXIT_BUTTON_BB = BoundingBox(362, 0, 38, 28)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
   
        self.yes_button: Button = Button(self.YES_BUTTON_BB, self.reset_backup())
        self.no_button: Button = Button(self.NO_BUTTON_BB, self.close())
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB, self.close())


    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }
    
    def reset_backup(self):
        """
        """

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
        elif self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)
        elif self.exit_button.is_clicked_by(click_position):
            self.exit_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]
        