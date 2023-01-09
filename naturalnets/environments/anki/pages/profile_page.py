import numpy as np
import os
from downgrade_popup_page import DowngradePopupPage
from choose_deck_study_page import ChooseDeckStudyPage
from add_card_page import AddCardPage
from anki_login_page import AnkiLoginPage
from export_page import ExportPage
from pages.choose_deck_page import ChooseDeckPage
from pages.delete_check_popup_page import DeleteCheckPopupPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase
from naturalnets.environments.anki.deck import DeckDatabase

class ProfilePage(Page,RewardElement):
    
    STATE_LEN = 6
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

        self.downgrade_and_quit_popup = Button(self.DOWNGRADE_QUIT_BB,)
        self.open_backup_button = Button(self.OPEN_BACKUP_BB,)
        self.delete_button = Button(self.DELETE_BB,)
        self.quit_button = Button(self.QUIT_BB,)
        self.rename_button = Button(self.RENAME_BB,)
        self.add_button = Button(self.ADD_BB,)
        self.open_button = Button(self.OPEN_BB,)

        self.current_index = 0
        self.profile = ProfileDatabase().profiles[0]

    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (384,22)
        # Box containing the items has size (386,423)
        # Top left corner (11,48)
        current_bounding_box = self.calculate_current_bounding_box()
        if(not(current_bounding_box.is_point_inside(click_point))):
            print("Point not inside the profiles bounding box")
            return
        else:
            click_index: int = click_point[1]/22
            self.current_index = click_index
            self.profile = ProfileDatabase().profiles[self.current_index]

    def calculate_current_bounding_box(self):
       upper_left_point = (11,48)
       length = 22 * DeckDatabase().decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 386, length)
       return current_bounding_box
    
    def delete_profile(self):
        ProfileDatabase().profiles.remove(self.profile)

    def reset_all(self):
        ProfileDatabase().reset_profiles()
        DeckDatabase().reset_decks()
        ChooseDeckStudyPage().reset_index()
        ChooseDeckPage().reset_index()
        AddCardPage().reset_all()
        AnkiLoginPage().reset()
        ExportPage().reset_current_deck()
    
    def open(self):
        self.get_state()[0] = 1
    
    def close(self):
        self.get_state()[0] = 0
    
    def is_open(self):
        return self.get_state()[0]