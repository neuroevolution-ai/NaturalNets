import os
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki import DeckDatabase
from naturalnets.environments.anki import ProfileDatabase
from naturalnets.environments.anki import ChooseDeckStudyPage
from naturalnets.environments.anki import AnkiLoginPage
from naturalnets.environments.anki import AddCardPage
from naturalnets.environments.anki import ChooseDeckPage
from naturalnets.environments.anki import ExportDeckPage
from naturalnets.environments.anki import ChooseDeckStudyPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class ResetCollectionPopupPage(Page, RewardElement):
    """
    State description:
            state[0]: if this window is open
    """
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "reset_collection.png")

    BOUNDING_BOX = BoundingBox(20, 20, 400, 120)
    YES_BUTTON_BB = BoundingBox(194, 106, 90, 26)
    NO_BUTTON_BB = BoundingBox(296, 106, 90, 26)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
   
        self.yes_button: Button = Button(self.YES_BUTTON_BB, self.reset_all)
        self.no_button: Button = Button(self.NO_BUTTON_BB, self.close)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ResetCollectionPopupPage, cls).__new__(cls)
        return cls.instance
    
    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"],
            "reset":"true"
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
        elif self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]
    
    def reset_all(self):
        ProfileDatabase().reset_profiles()
        DeckDatabase().reset_decks()
        ChooseDeckStudyPage().reset_index()
        ChooseDeckPage().reset_index()
        AddCardPage().reset_temporary_strings()
        AnkiLoginPage().reset()
        ExportDeckPage().reset_current_deck()
        self.register_selected_reward(["reset","true"])
        self.close()
    
    def render(self, img:np.ndarray):
        img = super().render(img)
        return img