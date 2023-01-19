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

    WINDOW_BB = BoundingBox(100, 100, 555, 466)
    OPEN_BB = BoundingBox(448, 112, 96, 24)
    ADD_BB = BoundingBox(448, 151, 96, 24)
    RENAME_BB = BoundingBox(448, 190, 96, 24)
    DELETE_BB = BoundingBox(448, 226, 96, 24)
    OPEN_BACKUP_BB = BoundingBox(448, 488, 96, 24)
    DOWNGRADE_QUIT_BB = BoundingBox(448, 526, 96, 24)
    PROFILES_BB = BoundingBox(98, 112, 340, 440)

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
        self.rename_button = Button(self.RENAME_BB, self.rename_profile_page.open)
        self.add_button = Button(self.ADD_BB, self.add_profile_popup_page.open)
        self.open_button = Button(self.OPEN_BB, self.close)
        
        self.profile_database.current_index: int = 0
        self.current_profile: Profile = self.profile_database.profiles[self.profile_database.current_index]

        self.set_reward_children([self.add_profile_popup_page, self.rename_profile_page, self.delete_profile_popup_page,
            self.reset_collection_popup_page, self.downgrade_popup_page, self.at_least_one_profile_popup_page])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "selected_profile_index": [0, 1, 2, 3, 4]
        }

    def change_current_deck_index(self, click_point:np.ndarray):
        current_bounding_box = self.calculate_current_bounding_box()
        if(current_bounding_box.is_point_inside(click_point)):
            click_index: int = floor((click_point[1] - 112) / 30)
            self.profile_database.current_index: int = click_index
            self.current_profile = self.profile_database.profiles[self.profile_database.current_index]
            self.get_state()[click_index + 1] = 1
            self.register_selected_reward(["selected_profile_index", click_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (97, 112)
       length = 30 * self.profile_database.profiles_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 340, length)
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
        put_text(img, f"Current profile: {self.profile_database.profiles[self.profile_database.current_index].name}", (518, 278), font_scale = 0.35)
        for i, profile in enumerate(self.profile_database.profiles):
            put_text(img, f"{profile.name}", (125, 102 + (i + 1) * 30), font_scale = 0.5)
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
        if self.add_profile_popup_page.is_open():
            self.add_profile_popup_page.handle_click(click_position)
            return
        elif self.rename_profile_page.is_open():
            self.rename_profile_page.handle_click(click_position)
            return
        elif self.delete_profile_popup_page.is_open():
            self.delete_profile_popup_page.handle_click(click_position)
            return
        elif self.reset_collection_popup_page.is_open():
            self.reset_collection_popup_page.handle_click(click_position)
            return
        elif self.downgrade_popup_page.is_open():
            self.downgrade_popup_page.handle_click(click_position)
            return
        elif self.at_least_one_profile_popup_page.is_open():
            self.at_least_one_profile_popup_page.handle_click(click_position)
            return
        elif self.calculate_current_bounding_box().is_point_inside(click_position):
            self.change_current_deck_index(click_position)
            return
        elif self.downgrade_and_quit_popup.is_clicked_by(click_position):
            self.downgrade_and_quit_popup.handle_click(click_position)
            return
        elif self.open_backup_button.is_clicked_by(click_position):
            self.open_backup_button.handle_click(click_position)
            return
        elif self.delete_button.is_clicked_by(click_position):
            self.delete_button.handle_click(click_position)
            return
        elif self.rename_button.is_clicked_by(click_position):
            self.rename_button.handle_click(click_position)
            return
        elif self.add_button.is_clicked_by(click_position):
            self.add_button.handle_click(click_position)
            return
        elif self.open_button.is_clicked_by(click_position):
            self.open_button.handle_click(click_position)
            return


class DeleteProfilePopupPage(Page,RewardElement):
    """
    State description:
        state[0]: if this window is open  
    """
    STATE_LEN = 1
    WINDOW_BB = BoundingBox(110, 240, 530, 113)
    IMG_PATH = os.path.join(IMAGES_PATH, "delete_profile_popup.png")
    YES_BUTTON_BB = BoundingBox(376, 316, 77, 24)
    NO_BUTTON_BB = BoundingBox(459, 316, 77, 24)

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
            self.profile_database.delete_profile()
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
    WINDOW_BB = BoundingBox(130, 250, 471, 121)
    IMG_PATH = os.path.join(IMAGES_PATH, "downgrade_popup.png")
    OK_BUTTON_BB = BoundingBox(402, 330, 98, 27)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DowngradePopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.ok_button = Button(self.OK_BUTTON_BB, self.close)
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
    WINDOW_BB = BoundingBox(190, 250, 318, 121)
    OK_BB = BoundingBox(342, 331, 77, 24)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FiveProfilesPopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.ok_button = Button(self.OK_BB, self.close)
    
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
    
    WINDOW_BB = BoundingBox(130, 250, 498, 111)
    OK_BB = BoundingBox(359, 320, 75, 24)
    TEXT_BB = BoundingBox(450, 290, 71, 21)
    CANCEL_BB = BoundingBox(444, 322, 75, 24)

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

        self.current_text = None
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
            self.close()
    
    def render(self,img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img,"" if self.current_field_string is None else f"{self.current_field_string}", (146 , 304), font_scale = 0.5)
        return img

class AddProfilePopupPage(Page,RewardElement):

    """
    State description:
        state[0]: if this popup is open
        state[1]: if the text field is filled
    """
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "add_profile_popup.png")
    
    WINDOW_BB = BoundingBox(112, 252, 500, 111)
    OK_BB = BoundingBox(343, 323, 78, 23)
    TEXT_BB = BoundingBox(433, 290, 73, 20)
    CANCEL_BB = BoundingBox(429, 324, 78, 23)

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

        self.add_children([self.name_exists_popup, self.five_profiles_popup])
        self.set_reward_children([self.name_exists_popup, self.five_profiles_popup])

    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            "profile_name_clipboard": 0
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if(self.name_exists_popup.is_open()):
            self.name_exists_popup.handle_click(click_position)
            return
        if(self.five_profiles_popup.is_open()):
            self.five_profiles_popup.handle_click(click_position)
            return
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
        put_text(img, "" if self.current_field_string is None else self.current_field_string, (130,306), font_scale = 0.5)
        if(self.five_profiles_popup.is_open()):
            img = self.five_profiles_popup.render(img)
        if(self.name_exists_popup.is_open()):
            img = self.name_exists_popup.render(img)
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
    WINDOW_BB = BoundingBox(200, 250, 318, 121)
    
    OK_BB = BoundingBox(350, 331, 76, 25)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AtLeastOneProfilePopupPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        self.ok_button: Button = Button(self.OK_BB, self.close)

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