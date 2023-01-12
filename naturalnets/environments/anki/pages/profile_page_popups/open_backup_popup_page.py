import os

import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.deck import DeckDatabase
from naturalnets.environments.anki.profile import ProfileDatabase
from choose_deck_study_page import ChooseDeckStudyPage
from pages.anki_login_page import AnkiLoginPage
from anki.pages.add_card_page import AddCardPage
from anki.pages.choose_deck_page import ChooseDeckPage
from export_page import ExportPage
from choose_deck_study_page import ChooseDeckStudyPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button

class OpenBackupPopup(Page, RewardElement):

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH,"open_backup_popup.png")

    BOUNDING_BOX = BoundingBox(30, 200, 400, 121)
    YES_BUTTON_BB = BoundingBox(223, 280, 90, 26)
    NO_BUTTON_BB = BoundingBox(326, 280, 90, 26)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
   
        self.yes_button: Button = Button(self.YES_BUTTON_BB, self.reset_all())
        self.no_button: Button = Button(self.NO_BUTTON_BB, self.close())

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenBackupPopup, cls).__new__(cls)
        return cls.instance
    
    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"],
            "set_to_default":"true"
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
        ProfileDatabase().default_profiles()
        DeckDatabase().default_decks()
        ChooseDeckStudyPage().reset_index()
        ChooseDeckPage().reset_index()
        AddCardPage().reset_all()
        AnkiLoginPage().default_login()
        ExportPage().reset_current_deck()
        self.register_selected_reward(["set_to_default","true"])
        self.close()
        