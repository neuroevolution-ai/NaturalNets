import random
import string
import numpy as np
import os

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import put_text
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import Profile,ProfileDatabase
class ProfilePage(Page,RewardElement):
    
    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "profile_page_ss.png")

    WINDOW_BB = BoundingBox(0, 0, 530, 482)
    OPEN_BB = BoundingBox(406, 50, 110, 26)
    ADD_BB = BoundingBox(406, 86, 110, 26)
    RENAME_BB = BoundingBox(406, 122, 110, 26)
    DELETE_BB = BoundingBox(406, 158, 110, 26)
    QUIT_BB = BoundingBox(406, 194, 110, 26)
    OPEN_BACKUP_BB = BoundingBox(410, 410, 110, 26)
    DOWNGRADE_QUIT_BB = BoundingBox(410, 446, 110, 26)
    PROFILES_BB = BoundingBox(11, 48, 386, 423)
    UP_BB = BoundingBox(374, 48, 19, 21)
    DOWN_BB = BoundingBox(374, 447, 19, 21)

    #Profiles in the profiles_bb have the (heigth,width) (384,22)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProfilePage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.profile_database = ProfileDatabase()

        self.add_profile_popup = AddProfilePopup()
        self.rename_profile_popup = RenameProfilePopup()
        self.at_least_one_profile_popup = AtLeastOneProfilePopup()
        self.delete_check_popup = DeleteCheckPopup()
        self.downgrade_popup = DowngradePopup()
        self.open_backup_popup = OpenBackupPopup()

        self.add_button: Button = Button(self.ADD_BB, self.add_profile_popup.open)
        self.rename_profile_button: Button = Button(self.RENAME_BB, self.rename_profile_popup.open)
        self.delete_button: Button = Button(self.DELETE_BB, self.delete_check_popup.open)
        self.quit_button: Button = Button(self.QUIT_BB,self.reset)
        self.open_backup_button: Button = Button(self.OPEN_BACKUP_BB, self.open_backup_popup.open)
        self.downgrade_quit_button: Button = Button(self.DOWNGRADE_QUIT_BB, self.downgrade_popup.open)
        
        self.add_children(
            [self.add_profile_popup,self.rename_profile_popup,self.at_least_one_profile_popup,
            self.delete_check_popup,self.downgrade_popup,self.open_backup_popup])

    @property
    def reward_template(self):
        return {
            "open_button": {
                "opened": 0,
            },
            "add_button": {
                "opened": 0,
            },
            "rename_button": {
                "opened": 0,
            },
            "delete_button": {
                "opened": 0,
            },
            "quit_button": {
                "opened": 0,
            },
            "open_backup_button": {
                "opened": 0,
            },
            "downgrade_button": {
                "opened": 0,
            },
        }


    def reset(self):
        self.add_profile_popup.close()
        self.rename_profile_popup.close()
        self.at_least_one_profile_popup.close()
        self.delete_check_popup.close()
        self.downgrade_popup.close()
        self.open_backup_popup.close()
        self.profile_database.reset_profiles()

    def scroll_down(self):
        if self.profile_database.is_scrollable and self.profile_database.scrolled_amount + 1 <= self.profile_database.profiles_length:
            self.profile_database.scrolled_amount += 1
    
    def scroll_up(self):
        if self.profile_database.is_scrollable and self.profile_database.scrolled_amount > 0:
            self.profile_database.scrolled_amount -= 1


class AddProfilePopup(Page, RewardElement):
    
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(12, 166, 501, 149)
    IMG_PATH = os.path.join(IMAGES_PATH, "add_profile_popup.png")
    OK_BUTTON_BB = BoundingBox(308, 276, 91, 26)
    CANCEL_BUTTON_BB = BoundingBox(408, 276, 91, 26)
    EXIT_BUTTON_BB = BoundingBox(474, 168, 42, 38)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
        self.cancel_button: Button = Button(self.CANCEL_BUTTON_BB, self.close)
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB,self.close)
        self.ok_button: Button = Button(self.OK_BUTTON_BB, ProfilePage().add_profile)
    
    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.cancel_button.is_clicked_by(click_position):
            self.cancel_button.handle_click(click_position)
        elif self.exit_button.is_clicked_by(click_position):
            self.exit_button.handle_click(click_position)
        elif self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]

class RenameProfilePopup(Page, RewardElement):
    
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(12, 166, 501, 149)
    IMG_PATH = os.path.join(IMAGES_PATH, "rename_profile_popup.png")
    OK_BUTTON_BB = BoundingBox(308, 276, 91, 26)
    CANCEL_BUTTON_BB = BoundingBox(408, 276, 91, 26)
    EXIT_BUTTON_BB = BoundingBox(474, 168, 42, 38)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
        self.cancel_button: Button = Button(self.CANCEL_BUTTON_BB, self.close)
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB,self.close)
        self.ok_button: Button = Button(self.OK_BUTTON_BB, ProfilePage().rename_profile)

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.cancel_button.is_clicked_by(click_position):
            self.cancel_button.handle_click(click_position)
        elif self.exit_button.is_clicked_by(click_position):
            self.exit_button.handle_click(click_position)
        elif self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]

class AtLeastOneProfilePopup(Page, RewardElement):
    
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(99, 167, 318, 145)
    IMG_PATH = os.path.join(IMAGES_PATH, "at_least_one_profile_popup.png")
    EXIT_BUTTON_BB = BoundingBox(377, 167, 42, 31)
    OK_BUTTON_BB = BoundingBox(311, 272, 91, 26)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB,self.close)
        self.ok_button: Button = Button(self.OK_BUTTON_BB,ProfilePage().rename_profile)

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }
    
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.exit_button.is_clicked_by(click_position):
            self.exit_button.handle_click(click_position)
        elif self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["popup", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]


class DeleteCheckPopup(Page, RewardElement):

    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(0, 168, 530, 135)
    IMG_PATH = os.path.join(IMAGES_PATH, "delete_check.png")
    YES_BUTTON_BB = BoundingBox(334, 265, 87, 24)
    NO_BUTTON_BB = BoundingBox(430, 265, 87, 24)
    EXIT_BUTTON_BB = BoundingBox(491, 168, 39, 35)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
        self.yes_button: Button = Button(self.YES_BUTTON_BB,ProfilePage().delete_profile)
        self.no_button: Button = Button(self.NO_BUTTON_BB,self.close)
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB,self.close)

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
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
        self.register_selected_reward(["popup", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]

class DowngradePopup(Page, RewardElement):
    
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(23, 166, 472, 147)
    IMG_PATH = os.path.join(IMAGES_PATH, "downgrade_popup.png")
    OK_BUTTON_BB = BoundingBox(389, 271, 91, 26)
    EXIT_BUTTON_BB = BoundingBox(456, 165, 42, 30)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
        self.ok_button: Button = Button(self.OK_BUTTON_BB, self.close)
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB, self.close)

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
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

class OpenBackupPopup(Page, RewardElement):

    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(59, 166, 402, 147)
    IMG_PATH = os.path.join(IMAGES_PATH,"open_backup_popup.png")
    YES_BUTTON_BB = BoundingBox(253, 272, 90, 26)
    NO_BUTTON_BB = BoundingBox(354, 272, 90, 26)
    EXIT_BUTTON_BB = BoundingBox(419, 166, 42, 30)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)
        self.yes_button: Button = Button(self.YES_BUTTON_BB, self.reset_backup)
        self.no_button: Button = Button(self.NO_BUTTON_BB, self.close)
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB, self.close)


    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"]
        }
    
    def reset_backup(self):
        ProfilePage().reset()
        self.close()

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
        