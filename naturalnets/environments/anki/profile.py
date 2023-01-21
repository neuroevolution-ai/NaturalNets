from typing import Final
from naturalnets.environments.anki import ProfileNames

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
        self.profile_names: Final = [ProfileNames.ALICE.value, ProfileNames.BOB.value, ProfileNames.CAROL.value, ProfileNames.DENNIS.value, ProfileNames.EVA.value]
        self.profiles = [Profile(ProfileNames.ALICE.value)]
        self.current_index: int = 0
    
    def is_adding_allowed(self) -> bool :
        return self.profiles_length() < 5 

    def is_removing_allowed(self) -> bool:
        return self.profiles_length() > 1 
    
    def profiles_length(self) -> int:
        return len(self.profiles)

    def create_profile(self,profile_name: str) -> None:
        self.profiles.append(Profile(profile_name))

    def rename_profile(self, new_name: str) -> None:
        self.profiles[self.current_index].name = new_name
    
    def delete_profile(self) -> None:
        for profile in self.profiles:
            if profile.name == self.profiles[self.current_index].name:
                self.profiles.remove(profile)
                self.current_index = 0

    def is_included(self,name: str) -> bool:
        for profile_temp in self.profiles:
            if profile_temp.name == name:
                return True      
        return False

    
    def reset_profiles(self) -> None:
        self.profiles = [Profile(ProfileNames.ALICE)]
        self.current_index: int = 0
        
    def default_profiles(self) -> None:
        self.profiles = [Profile(ProfileNames.ALICE.value), Profile(ProfileNames.BOB.value), Profile(ProfileNames.CAROL.value)]
        self.current_index: int = 1