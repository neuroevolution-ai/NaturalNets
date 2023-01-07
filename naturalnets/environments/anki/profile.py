import random
import numpy as np
from naturalnets.environments.anki.constants import ProfileNames,OptionNames,DeckNames
from naturalnets.environments.anki.deck import Deck, DeckOption
from naturalnets.environments.gui_app.bounding_box import BoundingBox

class Profile():
    
    def __init__(self, profile_name: str):
        self.name = profile_name
        self.decks = []
    
class ProfileDatabase():

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProfileDatabase, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.secure_random = random.SystemRandom()
        self.profile_names = [ProfileNames.ALICE, ProfileNames.BOB, ProfileNames.CAROL, ProfileNames.DENNIS, ProfileNames.EVA]
        self.current_field_string = None
        self.profiles = [Profile("Profile 1")]
        self.active_profile = None
        self.current_index = 0
    
    def is_adding_profile_allowed(self) -> bool :
        return self.profiles_length < 5

    def profiles_length(self) -> int:
        return len(self.profiles)

    def add_profile(self) -> None:
        if self.current_field_string == None:
            return
        profile_name = self.current_field_string
        self.current_field_string = None
        if self.is_included(Profile(profile_name),self.profiles):
            print("Name exists!")
            return
        elif not(self.is_adding_profile_allowed()):
            print("Max length is exceeded")
            return
        else:
            self.profiles.insert(Profile(profile_name))

    def rename_profile(self, profile: Profile) -> None:
        if self.current_field_string == None:
            return
        new_name = self.current_field_string
        self.current_field_string = None
        if self.is_included(Profile(new_name),Profile(self.profiles)):
            print("Name already exists!")
        else:
            profile.name = new_name
    
    def delete_profile(self, profile_name: str) -> None:
        for profile in self.profiles:
            if self.profiles_length() == 1:
                print("At least one profile must be present")
                return
            if profile.name == profile_name:
                self.profiles.remove(profile)


    def is_included(profile: Profile,profiles: list[Profile]) -> bool:
        for profile_temp in profiles:
            if profile_temp.name == profile.name:
                return True      
        return False

    def change_current_profile_index(self, click_position:np.ndarray):
        ##Calculate the clicked profile with size (384,22)
        current_bounding_box = self.calculate_current_bounding_box()
        if(not(current_bounding_box.is_point_inside(click_position))):
            print("Point not inside the profiles bounding box")
            return
        else:
            click_index: int = click_position[1]/22
            self.current_index = click_index

    def change_active_profile(self):
        self.active_profile = self.profiles[self.current_index]
    
    def reset_profiles(self):
        self.profiles = [Profile("Profile 1")]
        self.active_profile = None
        self.current_index = 0

    def calculate_current_bounding_box(self):
        #Each profile item has the 2-dimension (384,22)
        upper_left_point = (11,49)
        length = 22 * self.profiles_length()
        current_bounding_box = BoundingBox(upper_left_point[0],upper_left_point[1],384,length)
        return current_bounding_box

    def set_current_field_string(self):
        self.current_field_string = self.secure_random.choice(self.profile_names)