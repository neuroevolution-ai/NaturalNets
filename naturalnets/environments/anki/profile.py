import random
from typing import Final
import numpy as np
from naturalnets.environments.anki.constants import ProfileNames,OptionNames,DeckNames
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
        self.profile_names: Final = [ProfileNames.ALICE, ProfileNames.BOB, ProfileNames.CAROL, ProfileNames.DENNIS, ProfileNames.EVA]
        self.profiles = [Profile(ProfileNames.ALICE)]
        self.active_profile = self.profiles[0]
        self.current_index = 0
    
    def is_adding_allowed(self) -> bool :
        return self.profiles_length() < 5 

    def is_removing_allowed(self):
        return self.profiles_length() > 1 
    
    def profiles_length(self) -> int:
        return len(self.profiles)

    def create_profile(self,profile_name: str) -> None:
            self.profiles.insert(Profile(profile_name))

    def rename_profile(self, new_name: str) -> None:
        self.active_profile.name = new_name
    
    def delete_profile(self) -> None:
        for profile in self.profiles:
            if profile.name == self.active_profile.name:
                self.profiles.remove(profile)

    def is_included(self,name: str) -> bool:
        for profile_temp in self.profiles:
            if profile_temp.name == name:
                return True      
        return False

    def change_active_profile(self):
        self.active_profile = self.profiles[self.current_index]
    
    def reset_profiles(self):
        self.profiles = [Profile(ProfileNames.ALICE)]
        self.current_index = 0
        self.active_profile = self.profiles[self.current_index]
        
    def default_profiles(self):
        self.profiles = [Profile(ProfileNames.ALICE),Profile(ProfileNames.BOB),Profile(ProfileNames.CAROL)]
        self.active_profile = self.profiles[1]
        self.current_index = 1