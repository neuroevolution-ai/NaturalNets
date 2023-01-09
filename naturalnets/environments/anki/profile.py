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
        self.profiles = [Profile(ProfileNames.ALICE)]
        self.active_profile = ProfileNames.ALICE
        self.current_index = 0
    
    def is_length_allowed(self) -> bool :
        return self.profiles_length < 5 

    def is_removing_allowed(self):
        return self.profiles_length == 1 
    
    def profiles_length(self) -> int:
        return len(self.profiles)

    def create_profile(self,profile_name: str) -> None:
            self.profiles.insert(Profile(profile_name))

    def rename_profile(self, profile: Profile) -> None:

                ""
    
    def delete_profile(self, profile_name: str) -> None:
        for profile in self.profiles:
            if profile.name == profile_name:
                self.profiles.remove(profile)


    def is_included(self,name: str) -> bool:
        for profile_temp in self.profiles:
            if profile_temp.name == name:
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
        self.profiles = [Profile(ProfileNames.ALICE)]
        self.current_index = 0
        self.active_profile = self.profiles[self.current_index]
        

    def calculate_current_bounding_box(self):
        #Each profile item has the 2-dimension (384,22)
        upper_left_point = (11,49)
        length = 22 * self.profiles_length()
        current_bounding_box = BoundingBox(upper_left_point[0],upper_left_point[1],384,length)
        return current_bounding_box
