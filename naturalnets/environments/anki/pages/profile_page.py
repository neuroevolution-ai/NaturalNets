from math import floor
import random
import string
import cv2
import numpy as np
import os
from naturalnets.environments.anki.pages.add_card_page import AddCardPage
from naturalnets.environments.anki.pages.anki_login_page import AnkiLoginPage
from naturalnets.environments.anki.pages.choose_deck_page import ChooseDeckPage
from naturalnets.environments.anki.pages.choose_deck_study_page import ChooseDeckStudyPage
from naturalnets.environments.anki.pages.export_deck_page import ExportDeckPage
from naturalnets.environments.anki.pages.name_exists_popup_page import NameExistsPopupPage
from naturalnets.environments.anki import ResetCollectionPopupPage
from naturalnets.environments.anki.profile import Profile
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
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
        self.profile_database = ProfileDatabase()
        
        self.add_children([self.add_profile_popup_page, self.rename_profile_page, self.delete_profile_popup_page,
            self.reset_collection_popup_page, self.downgrade_popup_page, self.at_least_one_profile_popup_page])
        
        self.downgrade_and_quit_popup = Button(self.DOWNGRADE_QUIT_BB, self.downgrade_popup_page.open)
        self.open_backup_button = Button(self.OPEN_BACKUP_BB, self.reset_collection_popup_page.open)
        self.delete_button = Button(self.DELETE_BB, self.handle_delete)
        self.quit_button = Button(self.QUIT_BB, None)
        self.rename_button = Button(self.RENAME_BB, self.rename_profile_page.open)
        self.add_button = Button(self.ADD_BB, self.add_profile_popup_page.open)
        self.open_button = Button(self.OPEN_BB, self.close)
        
        self.current_index: int = 0
        self.current_profile: Profile = self.profile_database.profiles[self.current_index]


    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "selected_profile_index": [0, 1, 2, 3, 4]
        }

    def change_current_deck_index(self, click_point:np.ndarray):
        # Items have size (384,22)
        # Box containing the items has size (386,423)
        # Top left corner (11,11)
        current_bounding_box = self.calculate_current_bounding_box()
        if(current_bounding_box.is_point_inside(click_point)):
            click_index: int = floor((click_point[1] - 11)/22)
            self.current_index: int = click_index
            self.current_profile = self.profile_database.profiles[self.current_index]
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
        if(not(self.profile_database.is_removing_allowed())):
            self.at_least_one_profile_popup_page.open()
        else:
            self.delete_profile_popup_page.open()

    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
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

    def handle_click(self, click_position: np.ndarray) -> None:
        """"""
class DeleteProfilePopupPage(Page,RewardElement):
    """
    State description:
        state[0]: if this window is open  
    """
    STATE_LEN = 1
    WINDOW_BB = BoundingBox(35, 210, 530, 113)
    IMG_PATH = os.path.join(IMAGES_PATH, "delete_profile_popup.png")
    YES_BUTTON_BB = BoundingBox(370, 285, 87, 24)
    NO_BUTTON_BB = BoundingBox(465, 285, 87, 24)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeleteProfilePopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.profile_database = ProfileDatabase()
        self.yes_button: Button = Button(self.YES_BUTTON_BB, self.delete_profile)
        self.no_button: Button = Button(self.NO_BUTTON_BB, self.close)

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "delete_profile": 0
        }


    def handle_click(self, click_position: np.ndarray) -> None:
        if self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
        elif self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def delete_profile(self):
        if(self.profile_database.is_removing_allowed()):
            self.profile_database.delete_profile(self.profile_database.profiles[ProfilePage().current_index])
            self.register_selected_reward(["delete_profile"])
            self.close()
    
    def render(self,img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img
      
class DowngradePopupPage(Page, RewardElement):
    
    """
    State description:
        state[0]: if this window is open  
    """
    STATE_LEN = 1
    WINDOW_BB = BoundingBox(30, 200, 472, 121)
    IMG_PATH = os.path.join(IMAGES_PATH, "downgrade_popup.png")
    OK_BUTTON_BB = BoundingBox(395, 280, 91, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DowngradePopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def render(self,img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img

class FiveProfilesPopupPage(Page,RewardElement):

    """
    State description:
        state[0]: if this window is open  
    """
    
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "five_profiles_popup.png")
    WINDOW_BB = BoundingBox(30, 200, 318, 121)
    OK_BB = BoundingBox(242, 280, 92, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FiveProfilesPopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.ok_button.is_clicked_by(click_position)):
            self.ok_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]
    
    def render(self,img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img

class OpenBackupPopupPage(Page, RewardElement):

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH,"open_backup_popup.png")

    WINDOW_BB = BoundingBox(30, 200, 400, 121)
    YES_BUTTON_BB = BoundingBox(223, 280, 90, 26)
    NO_BUTTON_BB = BoundingBox(326, 280, 90, 26)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.profile_database = ProfileDatabase()
        self.deck_database = DeckDatabase()
        self.choose_deck_study_page = ChooseDeckStudyPage()
        self.choose_deck_page = ChooseDeckPage()   
        self.add_card_page = AddCardPage()
        self.anki_login_page = AnkiLoginPage()
        self.export_deck_page = ExportDeckPage()
        
        self.yes_button: Button = Button(self.YES_BUTTON_BB, self.reset_all)
        self.no_button: Button = Button(self.NO_BUTTON_BB, self.close)
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenBackupPopupPage, cls).__new__(cls)
        return cls.instance
    
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "set_to_default": 0
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
        elif self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]
    
    def reset_all(self):
        self.profile_database.default_profiles()
        self.deck_database.default_decks()
        self.choose_deck_study_page.reset_index()
        self.choose_deck_page.reset_index()
        self.add_card_page.reset_temporary_strings()
        self.anki_login_page.default_login()
        self.export_deck_page.reset_current_deck()
        self.register_selected_reward(["set_to_default"])
        self.close()
    
    def render(self,img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img

class RenameProfilePage(RewardElement,Page):
    
    """
    State description:
        state[0]: if this popup is open
        state[1]: if the text field is filled
    """

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "rename_profile_popup.png")
    
    WINDOW_BB = BoundingBox(30, 200, 498, 111)
    OK_BB = BoundingBox(323, 270, 91, 26)
    TEXT_BB = BoundingBox(430, 238, 86, 22)
    CANCEL_BB = BoundingBox(424, 270, 92, 27)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(RenameProfilePage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.profile_database = ProfileDatabase()
        self.name_exists_popup_page = NameExistsPopupPage()
        
        self.secure_random = random.SystemRandom()
        self.current_field_string = None
        
        self.text_button: Button = Button(self.TEXT_BB, self.set_current_field_string)
        self.ok_button: Button = Button(self.OK_BB, self.rename_profile)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)

        self.add_child(self.name_exists_popup_page)

    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "profile_name_clipboard": 0
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.text_button.is_clicked_by(click_position)):
            self.text_button.handle_click(click_position)
        elif(self.ok_button.is_clicked_by(click_position)):
            self.ok_button.handle_click(click_position)
        elif(self.cancel_button.is_clicked_by(click_position)):
            self.cancel_button.handle_click(click_position)

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])
    
    def set_current_field_string(self):
        self.current_field_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self.register_selected_reward(["profile_name_clipboard"])
    
    def is_open(self) -> int:
        return self.get_state()[0]

    def rename_profile(self):
        if (self.current_field_string is None):
            return
        if (self.profile_database.is_included(self.current_field_string)):
            self.name_exists_popup_page.open()
        else:
            self.profile_database.rename_profile(self.current_field_string)
    
    def render(self,img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img

class AddProfilePopupPage(Page,RewardElement):

    """
    State description:
        state[0]: if this popup is open
        state[1]: if the text field is filled
    """
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "add_profile_popup.png")
    
    WINDOW_BB = BoundingBox(30, 200, 500, 111)
    OK_BB = BoundingBox(322, 270, 91, 26)
    TEXT_BB = BoundingBox(430, 238, 86, 22)
    CANCEL_BB = BoundingBox(423, 270, 92, 27)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AddProfilePopupPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.name_exists_popup = NameExistsPopupPage()
        self.five_profiles_popup = FiveProfilesPopupPage()
        self.profile_database = ProfileDatabase()
        self.add_child(self.name_exists_popup)
        self.add_child(self.five_profiles_popup)

        self.secure_random = random.SystemRandom()
        self.current_field_string = None
        
        self.text_button: Button = Button(self.TEXT_BB, self.set_current_field_string)
        self.ok_button: Button = Button(self.OK_BB, self.add_profile)
        self.cancel_button: Button = Button(self.CANCEL_BB, self.close)

    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "profile_name_clipboard": 0
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.text_button.is_clicked_by(click_position)):
            self.text_button.handle_click(click_position)
        elif(self.ok_button.is_clicked_by(click_position)):
            self.ok_button.handle_click(click_position)
        elif(self.cancel_button.is_clicked_by(click_position)):
            self.cancel_button.handle_click(click_position)

    def close(self):
        self.get_state()[0] = 0
        self.get_state()[1] = 0
        self.register_selected_reward(["window", "close"])
        self.current_field_string = None
    
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])
    
    def set_current_field_string(self):
        self.get_state()[1] = 1
        self.register_selected_reward(["profile_name_clipboard"])
        self.current_field_string = self.secure_random.choice(self.profile_database.profile_names)
    
    def add_profile(self):
        if (self.current_field_string is None):
            return
        elif (not(self.profile_database.is_adding_allowed())):
            self.five_profiles_popup.open()
        elif (self.profile_database.is_included(self.current_field_string)):
            self.name_exists_popup.open()
        else:    
            self.profile_database.create_profile(self.current_field_string)
            self.current_field_string = None
            self.close()
            
    def render(self,img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img

    def is_open(self) -> int:
        return self.get_state()[0]

class AtLeastOneProfilePopupPage(Page, RewardElement):
    """
    State description:
        state[0]: if this popup is open
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "at_least_one_profile_popup.png")
    WINDOW_BB = BoundingBox(30, 200, 318, 121)
    
    OK_BUTTON_BB = BoundingBox(242, 281, 91, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AtLeastOneProfilePopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }
    
    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])

    def is_open(self) -> int:
        return self.get_state()[0]

    def render(self, img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img