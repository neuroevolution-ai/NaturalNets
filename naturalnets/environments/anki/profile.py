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