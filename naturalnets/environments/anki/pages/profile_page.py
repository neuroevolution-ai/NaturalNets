from math import floor
import cv2
import numpy as np
import os
from naturalnets.environments.anki.pages.profile_page_popups.add_profile_popup import AddProfilePopup
from naturalnets.environments.anki.pages.profile_page_popups.delete_profile_popup import DeleteProfilePopup
from naturalnets.environments.anki.pages.profile_page_popups.rename_profile_popup import RenameProfilePopup
from naturalnets.environments.anki.pages.profile_page_popups.downgrade_popup import DowngradePopup
from naturalnets.environments.anki.pages.profile_page_popups.at_least_one_profile_popup import AtLeastOneProfilePopup
from naturalnets.environments.anki.pages.reset_collection_popup import ResetCollectionPopup
from naturalnets.environments.anki.utils import calculate_current_bounding_box
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.profile import ProfileDatabase


class ProfilePage(Page, RewardElement):
    """
    Page to change the current profiles of the application.
    One can add,remove,rename a profile and change the currently active profile.
    Resetting the application is possible under the button "Open Backup". Downgrade
    button is actually a filler and does not affect the application logic
        State description:
            state[0]: if this window is open
            state[i]: there is a profile in the i-th position i = {1..5}
            state[i+5]: the profile in the i-th position is selected and active i = {1..5}
    """

    STATE_LEN = 11
    IMG_PATH = os.path.join(IMAGES_PATH, "profile_page.png")

    WINDOW_BB = BoundingBox(130, 150, 555, 466)
    OPEN_BB = BoundingBox(561, 167, 77, 25)
    ADD_BB = BoundingBox(561, 208, 77, 25)
    RENAME_BB = BoundingBox(561, 250, 77, 25)
    DELETE_BB = BoundingBox(561, 291, 77, 25)
    OPEN_BACKUP_BB = BoundingBox(522, 531, 117, 25)
    DOWNGRADE_QUIT_BB = BoundingBox(522, 577, 115, 25)
    PROFILES_BB = BoundingBox(143, 166, 403, 150)
    ITEM_WIDTH = 403
    ITEM_HEIGHT = 30
    TABLE_X = 143
    TABLE_Y = 166
    CURRENT_PROFILE_X = 507
    CURRENT_PROFILE_Y = 376
    PROFILE_TEXT_X = 152
    PROFILE_TEXT_Y = 189
    
    """
       Singleton design pattern to ensure that at most one
       ProfilePage is present
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProfilePage, cls).__new__(cls)
        return cls.instance

    def __init__(self):

        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.profile_database = ProfileDatabase()
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        self.current_index = 0
        # Popups of this page
        self.add_profile_popup_page = AddProfilePopup()
        self.rename_profile_page = RenameProfilePopup()
        self.delete_profile_popup_page = DeleteProfilePopup()
        self.reset_collection_popup_page = ResetCollectionPopup()
        self.downgrade_popup_page = DowngradePopup()
        self.at_least_one_profile_popup = AtLeastOneProfilePopup()
        # To display the current profiles profile database is necessary

        self.add_children([self.add_profile_popup_page, self.rename_profile_page, self.delete_profile_popup_page,
                           self.reset_collection_popup_page, self.downgrade_popup_page,
                           self.at_least_one_profile_popup])
        # Buttons of the profile page
        self.downgrade_and_quit_popup = Button(self.DOWNGRADE_QUIT_BB, self.downgrade_popup_page.open)
        self.open_backup_button = Button(self.OPEN_BACKUP_BB, self.reset_collection_popup_page.open)
        self.delete_button = Button(self.DELETE_BB, self.handle_delete)
        self.rename_button = Button(self.RENAME_BB, self.rename_profile_page.open)
        self.add_button = Button(self.ADD_BB, self.add_profile_popup_page.open)
        self.open_button = Button(self.OPEN_BB, self.close)

        # Index of the currently selected profile
        self.profile_database.set_current_index(0)
        self.pages = [self.add_profile_popup_page, self.rename_profile_page, self.delete_profile_popup_page, self.reset_collection_popup_page, self.downgrade_popup_page, self.at_least_one_profile_popup]

        self.button = [self.downgrade_and_quit_popup, self.open_backup_button, self.delete_button, self.rename_button, self.add_button, self.open_button]
        self.set_reward_children([self.add_profile_popup_page, self.rename_profile_page, self.delete_profile_popup_page,
                                  self.reset_collection_popup_page, self.downgrade_popup_page,
                                  self.at_least_one_profile_popup])
    """
    Provide reward for opening/closing window and changing the profile index
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "selected_profile_index": [0, 1, 2, 3, 4]
        }

    """
    Changes the current index regarding the selected profile if the click_point lies within 
    current_bounding_box.
    """
    def change_current_profile_index(self, click_point: np.ndarray):
        current_bounding_box = calculate_current_bounding_box(click_point[0], click_point[1], self.ITEM_HEIGHT, self.ITEM_WIDTH, self.profile_database.profiles_length())
        if current_bounding_box.is_point_inside(click_point):
            click_index: int = floor((click_point[1] - self.TABLE_Y) / self.ITEM_HEIGHT)
            if click_index >= self.profile_database.profiles_length():
                return
            self.current_index = click_index
            self.open_profile()

    """
    Opens this page
    """
    def open(self):
        self.get_state()[0] = 1
        self.reset_index()
        self.register_selected_reward(["window", "open"])

    """
    Closes this page
    """
    def close(self):
        self.get_state()[0] = 0
        self.reset_index()
        for child in self.get_children():
            child.close()
        self.register_selected_reward(["window", "close"])

    """
    Returns true if the profile page is open
    """
    def is_open(self):
        return self.get_state()[0]

    """
    If there are more than one profiles present delete profile popup
    is going to be opened else at least one profile popup
    """
    def handle_delete(self):
        if not (self.profile_database.is_removing_allowed()):
            self.at_least_one_profile_popup.open()
        else:
            self.delete_profile_popup_page.open()

    """
    Renders the profile page with it's popups if one is open
    """
    def render(self, img: np.ndarray):
        # Updates the deck database
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img, f"Selected profile: {self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_name()}",
                 (self.CURRENT_PROFILE_X, self.CURRENT_PROFILE_Y), font_scale=0.4)
        for i, profile in enumerate(self.profile_database.get_profiles()):
            put_text(img, f"{profile.get_name()}", (self.PROFILE_TEXT_X, self.PROFILE_TEXT_Y + i * self.ITEM_HEIGHT), font_scale=0.5)
        for page in self.pages:
            if page.is_open():
                img = page.render(img)
        return img

    """
    Delegate the click to a popup if open else handle click by buttons
    """
    def handle_click(self, click_position: np.ndarray) -> None:
        # Updates the deck database
        self.deck_database = self.profile_database.get_profiles()[self.profile_database.get_current_index()].get_deck_database()
        for page in self.pages:
            if page.is_open():
                page.handle_click(click_position)
                return
        for button in self.button:
            if button.is_clicked_by(click_position):
                button.handle_click(click_position)
                self.get_state()[1 : self.profile_database.profiles_length() + 1] = 1
                self.get_state()[self.profile_database.profiles_length() + 1 : 6] = 0
                return
        if calculate_current_bounding_box(self.TABLE_X, self.TABLE_Y, self.ITEM_HEIGHT, self.ITEM_WIDTH, self.profile_database.profiles_length()).is_point_inside(click_position):
            self.change_current_profile_index(click_position)
            return
    
    def open_profile(self):
        self.profile_database.set_current_index(self.current_index)
        self.get_state()[6:11] = 0
        self.get_state()[self.current_index + 6] = 1
        self.register_selected_reward(["selected_profile_index", self.current_index])
    
    def reset_index(self):
        self.current_index = 0
        self.get_state()[1:4] = 1
        self.get_state()[4:6] = 0
        self.get_state()[6] = 1
        self.get_state()[7:11] = 0
        