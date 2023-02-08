from math import floor
import random
import string
import cv2
import numpy as np
import os
from naturalnets.environments.anki.pages.name_exists_popup import NameExistsPopup
from naturalnets.environments.anki import ResetCollectionPopup
from naturalnets.environments.anki.profile import Profile
from naturalnets.environments.gui_app.utils import put_text, render_onto_bb
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki import ProfileDatabase

class ProfilePage(Page,RewardElement):
    """
    Page to change the current profiles of the application.

        State description:
            state[0]: if this window is open
            state[i]: i-th menu item of the profiles bounding-box (6 > i > 0)
    """
    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "profile_page.png")

    WINDOW_BB = BoundingBox(130, 150, 555, 466)
    OPEN_BB = BoundingBox(561, 167, 77, 25)
    ADD_BB = BoundingBox(561, 208, 77, 25)
    RENAME_BB = BoundingBox(561, 250, 77, 25)
    DELETE_BB = BoundingBox(561, 291, 77, 25)
    OPEN_BACKUP_BB = BoundingBox(522, 531, 117, 25)
    DOWNGRADE_QUIT_BB = BoundingBox(522, 577, 115, 25)
    PROFILES_BB = BoundingBox(143, 166, 403, 150)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProfilePage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.add_profile_popup_page = AddProfilePopup()
        self.rename_profile_page = RenameProfilePopup()
        self.delete_profile_popup_page = DeleteProfilePopup()
        self.reset_collection_popup_page = ResetCollectionPopup()
        self.downgrade_popup_page = DowngradePopup()
        self.at_least_one_profile_popup = AtLeastOneProfilePopup()
        self.profile_database = ProfileDatabase()
        
        self.add_children([self.add_profile_popup_page, self.rename_profile_page, self.delete_profile_popup_page,
            self.reset_collection_popup_page, self.downgrade_popup_page, self.at_least_one_profile_popup])
        
        self.downgrade_and_quit_popup = Button(self.DOWNGRADE_QUIT_BB, self.downgrade_popup_page.open)
        self.open_backup_button = Button(self.OPEN_BACKUP_BB, self.reset_collection_popup_page.open)
        self.delete_button = Button(self.DELETE_BB, self.handle_delete)
        self.rename_button = Button(self.RENAME_BB, self.rename_profile_page.open)
        self.add_button = Button(self.ADD_BB, self.add_profile_popup_page.open)
        self.open_button = Button(self.OPEN_BB, self.close)
        
        self.profile_database.current_index: int = 0
        self.current_profile: Profile = self.profile_database.profiles[self.profile_database.current_index]

        self.set_reward_children([self.add_profile_popup_page, self.rename_profile_page, self.delete_profile_popup_page,
            self.reset_collection_popup_page, self.downgrade_popup_page, self.at_least_one_profile_popup])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "selected_profile_index": [0, 1, 2, 3, 4]
        }

    def change_current_profile_index(self, click_point:np.ndarray):
        current_bounding_box = self.calculate_current_bounding_box()
        if(current_bounding_box.is_point_inside(click_point)):
            click_index: int = floor((click_point[1] - 166) / 30)
            if(click_index >= self.profile_database.profiles_length()):
                return
            self.get_state()[self.profile_database.current_index + 1] = 0
            self.profile_database.current_index: int = click_index
            self.current_profile = self.profile_database.profiles[self.profile_database.current_index]
            self.get_state()[click_index + 1] = 1
            self.register_selected_reward(["selected_profile_index", click_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (143, 166)
       length = 30 * self.profile_database.profiles_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 403, length)
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
            self.at_least_one_profile_popup.open()
        else:
            self.delete_profile_popup_page.open()

    def render(self, img: np.ndarray):
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img, f"Current profile: {self.profile_database.profiles[self.profile_database.current_index].name}", (507, 376), font_scale = 0.4)
        for i, profile in enumerate(self.profile_database.profiles):
            put_text(img, f"{profile.name}", (152, 189 + i * 30), font_scale = 0.5)
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
        elif self.at_least_one_profile_popup.is_open():
            img = self.at_least_one_profile_popup.render(img)
        return img

    def handle_click(self, click_position: np.ndarray) -> None:
        self.deck_database = self.profile_database.profiles[self.profile_database.current_index].deck_database
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
        elif self.at_least_one_profile_popup.is_open():
            self.at_least_one_profile_popup.handle_click(click_position)
            return
        elif self.calculate_current_bounding_box().is_point_inside(click_position):
            self.change_current_profile_index(click_position)
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


class DeleteProfilePopup(Page,RewardElement):
    """
    State description:
        state[0]: if this window is open  
    """
    STATE_LEN = 1
    WINDOW_BB = BoundingBox(160, 300, 530, 113)
    IMG_PATH = os.path.join(IMAGES_PATH, "delete_profile_popup.png")
    YES_BUTTON_BB = BoundingBox(478, 376, 84, 26)
    NO_BUTTON_BB = BoundingBox(586, 375, 84, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeleteProfilePopup, cls).__new__(cls)
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
      
class DowngradePopup(Page, RewardElement):
    
    """
    State description:
        state[0]: if this window is open

    """
    STATE_LEN = 1
    WINDOW_BB = BoundingBox(160, 300, 530, 113)
    IMG_PATH = os.path.join(IMAGES_PATH, "downgrade_popup.png")
    OK_BUTTON_BB = BoundingBox(601, 382, 81, 25)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DowngradePopup, cls).__new__(cls)
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

class FiveProfilesPopup(Page,RewardElement):

    """
    State description:
        state[0]: if this window is open  
    """
    
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "five_profiles_popup.png")
    WINDOW_BB = BoundingBox(230, 300, 318, 121)
    OK_BB = BoundingBox(462, 384, 78, 31)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FiveProfilesPopup, cls).__new__(cls)
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

class RenameProfilePopup(RewardElement,Page):
    
    """
    State description:
        state[0]: if this popup is open
        state[1]: if the text field is filled
    """

    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "rename_profile_popup.png")
    
    WINDOW_BB = BoundingBox(160, 305, 498, 111)
    OK_BB = BoundingBox(451, 381, 82, 24)
    TEXT_BB = BoundingBox(566, 345, 86, 20)
    CANCEL_BB = BoundingBox(549, 381, 101, 24)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(RenameProfilePopup, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.profile_database = ProfileDatabase()
        self.name_exists_popup_page = NameExistsPopup()
        
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
            "profile_name_clipboard": 0,
            "rename": 0
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
        self.current_field_string = None
    
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
            self.register_selected_reward(["rename"])
            self.close()
    
    def render(self,img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img, "" if self.current_field_string is None else self.current_field_string, (191,359), font_scale = 0.5)
        return img

class AddProfilePopup(Page,RewardElement):

    """
    State description:
        state[0]: if this popup is open
        state[1]: if the text field is filled
    """
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "add_profile_popup.png")
    
    WINDOW_BB = BoundingBox(160, 305, 498, 109)
    OK_BB = BoundingBox(451, 381, 82, 24)
    TEXT_BB = BoundingBox(566, 345, 86, 20)
    CANCEL_BB = BoundingBox(549, 381, 101, 24)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AddProfilePopup, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.name_exists_popup = NameExistsPopup()
        self.five_profiles_popup = FiveProfilesPopup()
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
            "profile_name_clipboard": 0,
            "add_profile": 0
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
            self.register_selected_reward(["add_profile"])
            self.close()
            
    def render(self,img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        put_text(img, "" if self.current_field_string is None else self.current_field_string, (191,359), font_scale = 0.5)
        if(self.five_profiles_popup.is_open()):
            img = self.five_profiles_popup.render(img)
        if(self.name_exists_popup.is_open()):
            img = self.name_exists_popup.render(img)
        return img

    def is_open(self) -> int:
        return self.get_state()[0]

class AtLeastOneProfilePopup(Page, RewardElement):
    """
    State description:
        state[0]: if this popup is open
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "at_least_one_profile_popup.png")
    WINDOW_BB = BoundingBox(200, 250, 318, 121)
    
    OK_BB = BoundingBox(427, 339, 81, 23)
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AtLeastOneProfilePopup, cls).__new__(cls)
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