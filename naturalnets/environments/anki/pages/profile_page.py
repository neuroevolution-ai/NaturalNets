import numpy as np
import os
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase

class ProfilePage(Page,RewardElement):
    
    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "profile_page.png")

    WINDOW_BB = BoundingBox(0, 0, 530, 482)
    OPEN_BB = BoundingBox(406, 50, 110, 26)
    ADD_BB = BoundingBox(406, 86, 110, 26)
    RENAME_BB = BoundingBox(406, 122, 110, 26)
    DELETE_BB = BoundingBox(406, 158, 110, 26)
    QUIT_BB = BoundingBox(406, 194, 110, 26)
    OPEN_BACKUP_BB = BoundingBox(410, 410, 110, 26)
    DOWNGRADE_QUIT_BB = BoundingBox(410, 446, 110, 26)
    PROFILES_BB = BoundingBox(11, 48, 386, 423)

    #Profiles in the profiles_bb have the (heigth,width) (384,22)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProfilePage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.profile_database = ProfileDatabase()

        self.rename_profile_popup = RenameProfilePopup()
        self.delete_check_popup = DeleteCheckPopup()
        self.downgrade_popup = DowngradePopup()
        self.open_backup_popup = OpenBackupPopup()

        self.open_button: Button = Button(self.OPEN_BB, self.open_button.switch_to_main_page)
        self.add_button: Button = Button(self.ADD_BB, self.add_profile_popup.open)
        self.rename_profile_button: Button = Button(self.RENAME_BB, self.rename_profile_popup.open)
        self.delete_button: Button = Button(self.DELETE_BB, self.delete_check_popup.open)
        self.quit_button: Button = Button(self.QUIT_BB,self.reset)
        self.open_backup_button: Button = Button(self.OPEN_BACKUP_BB, self.open_backup_popup.open)
        self.downgrade_quit_button: Button = Button(self.DOWNGRADE_QUIT_BB, self.downgrade_popup.open)
        
        self.add_children(
            [self.add_profile_popup,self.rename_profile_popup,self.at_least_one_profile_popup,
            self.delete_check_popup,self.downgrade_popup,self.open_backup_popup])

    def reset(self):
        self.add_profile_popup.close()
        self.rename_profile_popup.close()
        self.at_least_one_profile_popup.close()
        self.delete_check_popup.close()
        self.downgrade_popup.close()
        self.open_backup_popup.close()
        self.profile_database.reset_profiles()

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.add_button.is_clicked_by(click_position)):
            self.add_button.handle_click(click_position)
        elif(self.rename_profile_button.is_clicked_by(click_position)):
            self.rename_profile_button.handle_click(click_position)
        elif(self.delete_button.is_clicked_by(click_position)):
            self.delete_button.handle_click(click_position)
        elif(self.quit_button.is_clicked_by(click_position)):
            self.quit_button.handle_click(click_position)
        elif(self.open_backup_button.is_clicked_by(click_position)):
            self.open_backup_button.handle_click(click_position)
        elif(self.downgrade_quit_button.is_clicked_by(click_position)):
            self.downgrade_quit_button.is_clicked_by(click_position)
        elif(self.PROFILES_BB.is_point_inside(click_position)):
            ProfileDatabase().change_active_profile(click_position)

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
        self.open()
        self.cancel_button: Button = Button(self.CANCEL_BUTTON_BB, self.close)
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB,self.close)
        self.ok_button: Button = Button(self.OK_BUTTON_BB, ProfileDatabase().rename_profile)

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
        self.open()
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
        