import numpy as np
import os
from naturalnets.environments.anki.pages.profile_page_popups import RenameProfilePage
from naturalnets.environments.anki.pages import ResetCollectionPopupPage
from naturalnets.environments.anki.pages.profile_page_popups import AddProfilePopupPage
from naturalnets.environments.gui_app.utils import put_text
from naturalnets.environments.anki.pages.profile_page_popups import DowngradePopupPage
from naturalnets.environments.anki.pages.profile_page_popups import AtLeastOneProfilePopupPage
from naturalnets.environments.anki.pages.profile_page_popups import DeleteProfilePopupPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki import ProfileDatabase
from naturalnets.environments.anki import DeckDatabase

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

        self.add_profile_popup_page = AddProfilePopupPage()
        self.rename_profile_page = RenameProfilePage()
        self.delete_profile_popup_page = DeleteProfilePopupPage()
        self.reset_collection_popup_page = ResetCollectionPopupPage()
        self.downgrade_popup_page = DowngradePopupPage()
        self.at_least_one_profile_popup_page = AtLeastOneProfilePopupPage()
        
        self.add_children([self.add_profile_popup_page, self.rename_profile_page, self.delete_profile_popup_page,
            self.reset_collection_popup_page, self.downgrade_popup_page, self.at_least_one_profile_popup_page])
        
        self.downgrade_and_quit_popup = Button(self.DOWNGRADE_QUIT_BB, self.downgrade_popup_page.open())
        self.open_backup_button = Button(self.OPEN_BACKUP_BB, self.reset_collection_popup_page.open())
        self.delete_button = Button(self.DELETE_BB, self.handle_delete())
        self.quit_button = Button(self.QUIT_BB, self.register_selected_reward(["quit"]))
        self.rename_button = Button(self.RENAME_BB, self.rename_profile_page.open())
        self.add_button = Button(self.ADD_BB, self.add_profile_popup_page.open())
        self.open_button = Button(self.OPEN_BB, self.close())
        
        self.current_index = 0
        self.profile = None

        self.add_widgets([ self.downgrade_and_quit_popup, self.open_backup_button, self.delete_button, self.quit_button,
            self.rename_button, self.add_button, self.open_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "selected_profile_index": [0, 1, 2, 3, 4],
            "quit": 0,
        }

    def change_current_deck_index(self, click_point:np.ndarray):
        # Items have size (384,22)
        # Box containing the items has size (386,423)
        # Top left corner (11,11)
        current_bounding_box = self.calculate_current_bounding_box()
        if(current_bounding_box.is_point_inside(click_point)):
            click_index: int = (click_point[1] - 11)/22
            self.current_index = click_index
            self.profile = ProfileDatabase().profiles[self.current_index]
            self.get_state()[click_index + 1] = 1
            self.register_selected_reward(["selected_profile_index", click_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (11,11)
       length = 22 * DeckDatabase().decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 386, length)
       return current_bounding_box
    
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
            self.at_least_one_profile_popup_page.open()
        else:
            self.delete_profile_popup_page.open()

    def render(self, img: np.ndarray):
        img = super().render(img)
        for i, deck in enumerate(DeckDatabase().decks):
            put_text(img, deck.name, (11, 11 + (i + 1) * 22), font_scale = 0.3)
        if self.add_profile_popup_page.is_open():
            img = self.add_profile_popup_page.render(img)
        elif self.rename_profile_page.is_open():
            img = self.rename_profile_page.render(img)
        elif self.delete_profile_popup_page.is_open():
            img = self.delete_profile_popup_page.render(img)
        elif self.reset_collection_popup_page.is_open():
            img = self.reset_collection_popup_page.render(img)
        elif self.downgrade_popup_page.is_open():
            img = self.downgrade_popup_page.render(img)
        elif self.at_least_one_profile_popup_page.is_open():
            img = self.at_least_one_profile_popup_page.render(img)
        return img