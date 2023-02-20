import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button

class ResetCollectionPopup(Page, RewardElement):
    """
    Resets the application state to a predefined state
    with 3 default profiles and 2 decks for each profile
    State description:
            state[0]: if this window is open
    """
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "reset_collection_popup.png")

    BOUNDING_BOX = BoundingBox(160, 300, 530, 113)
    YES_BUTTON_BB = BoundingBox(478, 377, 82, 24)
    NO_BUTTON_BB = BoundingBox(586, 377, 84, 24)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        # Profile database to set to the default profiles with default decks
        self.profile_database = ProfileDatabase()
        self.yes_button: Button = Button(self.YES_BUTTON_BB, self.reset_all)
        self.no_button: Button = Button(self.NO_BUTTON_BB, self.close)

    """
        Singleton design pattern to ensure that at most one
        ResetCollectionPopup is present
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ResetCollectionPopup, cls).__new__(cls)
        return cls.instance

    """
    Provide reward for opening/closing this popup and for resetting the application
    """
    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"],
            "reset_all": 0
        }

    """
    Handle click with the buttons
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
        elif self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)
    """
    Open this popup
    """
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    """
    Close this popup
    """
    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    """
    Return true if this popup is open
    """
    def is_open(self) -> int:
        return self.get_state()[0]
    """
    Set the application to the default configuration
    """
    def reset_all(self):
        self.profile_database.default_profiles()
        for profile in self.profile_database.profiles:
            profile.deck_database.default_decks()
        self.register_selected_reward(["reset_all"])
        self.close()
    """
    Render this popup
    """
    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img
