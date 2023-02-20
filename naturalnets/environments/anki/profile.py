from typing import Final
from naturalnets.environments.anki.constants import ProfileNames
from naturalnets.environments.anki.deck import DeckDatabase


class Profile:
    """
    A profile is composed of a name and it's decks aka DeckDatabase
    """

    def __init__(self, profile_name: str):
        self.name = profile_name
        self.deck_database = DeckDatabase()

    def get_name(self):
        return self.name

    def get_deck_database(self):
        return self.deck_database

class ProfileDatabase:
    """
    This database contains the current profiles
    """

    """
    Singleton design pattern to ensure that at most one
    ProfileDatabase is present
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProfileDatabase, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.profile_names: Final = [ProfileNames.ALICE.value, ProfileNames.BOB.value, ProfileNames.CAROL.value,
                                     ProfileNames.DENNIS.value, ProfileNames.EVA.value]
        self.profiles = [Profile(ProfileNames.ALICE.value), Profile(ProfileNames.BOB.value), Profile(ProfileNames.CAROL.value)]
        self.current_index: int = 1
        
        for profile in self.profiles:
            profile.deck_database.default_decks()

    def get_current_index(self):
        return self.current_index

    def get_profile_names(self):
        return self.profile_names

    def get_profiles(self):
        return self.profiles

    def set_current_index(self, index: int):
        self.current_index = index

    """
    Adding a profile is allowed if there are less than 5 profiles
    """
    def is_adding_allowed(self) -> bool:
        return self.profiles_length() < 5

    """
    Removing a profile is allowed if there are more than 1 profiles
    """
    def is_removing_allowed(self) -> bool:
        return self.profiles_length() > 1

    """
    Returns the number of profiles
    """
    def profiles_length(self) -> int:
        return len(self.profiles)

    """
    Creates a new profile with profile_name and appends it to the list of profiles.
    """
    def create_profile(self, profile_name: str) -> None:
        profile = Profile(profile_name)
        profile.get_deck_database().default_decks()
        self.profiles.append(profile)

    """
    Changes the name of the current profile with a new name
    """
    def rename_profile(self, new_name: str) -> None:
        self.profiles[self.current_index].name = new_name

    """
    Deletes the profile of the current index.
    """
    def delete_profile(self) -> None:
        for profile in self.profiles:
            if profile.name == self.profiles[self.current_index].name:
                self.profiles.remove(profile)
                self.current_index = 0

    """
    Checks if a profile is included in the set of profiles
    """
    def is_included(self, name: str) -> bool:
        for profile_temp in self.profiles:
            if profile_temp.name == name:
                return True
        return False
    """
    Sets the current profiles of the application to a predefined set of profiles
    """
    def default_profiles(self) -> None:
        self.profiles = [Profile(ProfileNames.ALICE.value), Profile(ProfileNames.BOB.value),
                         Profile(ProfileNames.CAROL.value)]
        self.current_index: int = 0
