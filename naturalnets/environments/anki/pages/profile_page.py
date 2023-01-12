import numpy as np
import os
from main_page import MainPage
from profile_page_popups.at_least_one_profile_popup_page import AtLeastOneProfilePopupPage
from profile_page_popups.delete_check_popup_page import DeleteCheckPopupPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.anki.deck import DeckDatabase

class ProfilePage(Page,RewardElement):
    """
    Page to change the current profiles of the application.

        State description:
            state[0]: if this window is open
            state[i]: i-th menu item of the profiles bounding-box (6 > i > 0)
    """
    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "profile_page.png")

    WINDOW_BB = BoundingBox(0, 0, 528, 444)
    OPEN_BB = BoundingBox(406, 13, 110, 26)
    ADD_BB = BoundingBox(406, 49, 110, 26)
    RENAME_BB = BoundingBox(406, 85, 110, 26)
    DELETE_BB = BoundingBox(406, 121, 110, 26)
    QUIT_BB = BoundingBox(406, 157, 110, 26)
    OPEN_BACKUP_BB = BoundingBox(410, 373, 110, 26)
    DOWNGRADE_QUIT_BB = BoundingBox(410, 409, 110, 26)
    PROFILES_BB = BoundingBox(11, 11, 386, 423)

    #Profiles in the profiles_bb have the (heigth,width) (384,22)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProfilePage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.main_page = MainPage()

        self.downgrade_and_quit_popup = Button(self.DOWNGRADE_QUIT_BB,)
        self.open_backup_button = Button(self.OPEN_BACKUP_BB,)
        self.delete_button = Button(self.DELETE_BB, self.handle_delete())
        self.quit_button = Button(self.QUIT_BB, )
        self.rename_button = Button(self.RENAME_BB,)
        self.add_button = Button(self.ADD_BB,)
        self.open_button = Button(self.OPEN_BB,)

        self.delete_check_popup = DeleteCheckPopupPage()
        self.at_least_one_profile_popup = AtLeastOneProfilePopupPage()
        
        self.current_index = 0
        self.profile = ProfileDatabase().active_profile

    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "open_main_window": 0,
            "add_profile_popup": ["open","close"],
            "rename_profile_popup": ["open","close"],
            "delete_profile_popup": ["open","close"],
            "at_least_one_profile_popup": ["open","close"],
            "open_backup": ["open","close"],
            "reset_application": 0,
            "selected_profile_index": [0,1,2,3,4]
        }

    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (384,22)
        # Box containing the items has size (386,423)
        # Top left corner (11,11)
        current_bounding_box = self.calculate_current_bounding_box()
        if(current_bounding_box.is_point_inside(click_point)):
            click_index: int = click_point[1]/22
            self.current_index = click_index
            self.profile = ProfileDatabase().profiles[self.current_index]
            self.register_selected_reward(["selected_profile_index", click_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (11,11)
       length = 22 * DeckDatabase().decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 386, length)
       return current_bounding_box
    
    def delete_profile(self):
        ProfileDatabase().profiles.remove(self.profile)
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])
    
    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def is_open(self):
        return self.get_state()[0]

    def handle_delete(self):
        if(not(ProfileDatabase().is_removing_allowed())):
            self.at_least_one_profile_popup.open()
            self.register_selected_reward(["at_least_one_profile_popup","open"])
        else:
            self.delete_check_popup.open()
            self.register_selected_reward(["delete_profile_popup","open"])

    def open_main_page(self):
        self.close()
        self.main_page.open()
        self.register_selected_reward(["open_main_window"])