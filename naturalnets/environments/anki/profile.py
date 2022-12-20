from naturalnets.environments.anki.deck import Deck, DeckOption
import random
import string

class Profile():
    
    def __init__(self, profile_name: str):
        self.name = profile_name
        self.deck_list: list[Deck] = []
        self.deck_options : list[DeckOption] = [DeckOption("Default",True)]

    def count_deck_option_occurrences(self,deck_option: DeckOption):
        deck_option_occurrence: int = 0
        for deck in self.deck_list:
            if deck.current_option == deck_option:
                deck_option_occurrence += 1
        return deck_option_occurrence

    def __init__(self):
        self.available_deck_options: list[DeckOption] = [DeckOption("Default")]
    
    def add_option(self, deck_option: DeckOption):
        if not(self.check_occurrence(deck_option)):
            self.available_deck_options.append(deck_option)
        else:
            print("Option with same name already present")

    def remove_option(self, deck_option: DeckOption):
        if deck_option.is_default_option:
            print("The default configuration can not be removed")
            return

        for option in self.available_deck_options:
            if option.name == deck_option.name:
                self.available_deck_options.remove(option)

    def check_occurrence(self, deck_option: DeckOption) -> bool:
        for available_deck_option in self.available_deck_options:
            if available_deck_option.name == deck_option.name:
                return True
        
        return False    
      
    def rename_option(self, deck_option: DeckOption):
        # To avoid keyboard inputs renaming is randomized
        deck_option.name = ''.join(random.choices(string.ascii_lowercase, k=5))

class ProfileDatabase():

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProfileDatabase, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.profiles = [Profile("Profile 1")]
        self.active_profile = self.profiles[0]
        self.scrolled_amount = 0
    
    def add_profile(self) -> None:
        profile_name: str = ''.join(random.choices(string.ascii_lowercase, k=5))
        if not(self.is_included(Profile(profile_name),self.profiles)) :
            self.profiles.insert(Profile(profile_name))
        else:
            print("Name exists!")

    def rename_profile(self, profile: Profile) -> None:
        new_name: str = ''.join(random.choices(string.ascii_lowercase, k=5))
        if self.is_included(Profile(new_name),Profile(self.profiles)):
            print("Name already exists!")
            return
        profile.name = new_name
    
    def delete_profile(self, profile_name: str) -> None:
        for profile in self.profiles:
            if profile.name == profile_name:
                self.profiles.remove(profile)

    def profiles_length(self) -> int:
        return len(self.profiles)

    def is_included(profile: Profile,profiles: list[Profile]) -> bool:
        for profile_temp in profiles:
            if profile_temp.name == profile.name:
                return True      
        return False

    def change_active_profile(self,index:int):
        if index < len(self.profiles) and index >= 0 :
            self.active_profile = self.profiles[index]
        else:
            print("Index out of bounds")
    
    def reset_profiles(self):
        self.profiles = [Profile("Profile 1")]
        self.active_profile = self.profiles[0]
    
    def is_scrollable(self):
        return self.profiles_length >= 19