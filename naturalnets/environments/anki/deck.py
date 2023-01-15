from typing import List

from naturalnets.environments.anki.card import Card
from naturalnets.environments.anki.deck import Deck,DeckDatabase
from naturalnets.environments.anki.constants import DeckNames,DeckImportName,PREDEFINED_DECKS_PATH,EXPORTED_DECKS_PATH
import os

class Deck():
    
    def __init__(self,deck_name:str):
        self.name = deck_name
        self.cards: List[Card] = []
        self.current_card: Card = None
        self.study_index = 0
        
    
    def is_duplicate(self,card: Card):
        for current_card in self.cards:
            if(current_card is card):
                return True
        return False

    def add_card(self,card: Card):
        if(not(self.is_duplicate(card))):
            self.cards.append(card)
        
    def increment_study_index(self):
        if(self.study_index < len(self.cards)):
            self.study_index += 1 
        elif(self.study_index == len(self.cards)):
            self.study_index = 0
    
    def create_study(self):
        self.study_deck = self.study_deck

class DeckDatabase():

    #
    # Restrict the max number of decks and exported files by 5
    # 

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeckDatabase, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        
        self.deck_names = [DeckNames.DECK_NAME_1.value, DeckNames.DECK_NAME_2.value, DeckNames.DECK_NAME_3.value, DeckNames.DECK_NAME_4.value, DeckNames.DECK_NAME_5.value]
        self.deck_import_names = [DeckImportName.DUTCH_NUMBERS.value, DeckImportName.GERMAN_NUMBERS.value, DeckImportName.ITALIAN_NUMBERS.value]
        self.decks: List[Deck] = [Deck(DeckNames.DECK_NAME_1.value)]
        self.current_index = 0
        self.current_deck: Deck = self.decks[self.current_index]

    def decks_length(self):
        return len(self.decks)

    def is_deck_length_allowed(self):
        return self.decks_length() < 5

    def count_number_of_files(self,dir_path: str):
        count = 0
        for path in os.scandir(dir_path):
            if path.is_file():
                count += 1
        return count 
    
    def is_exporting_allowed(self):
        return self.count_number_of_files(EXPORTED_DECKS_PATH) < 5

    def fetch_deck(self,deck_name: str) -> Deck:
        for deck in self.decks:
            if(deck_name == deck.name):
                return deck
        return None

    def is_included(self,deck_name: str):
        return self.fetch_deck(deck_name) is not None
    
    def create_deck(self,deck_name:str):
        self.decks.append(Deck(deck_name))
    
    def import_deck(self,deck_import_name: str):
        path = os.path.join(PREDEFINED_DECKS_PATH, deck_import_name + ".txt")
        deck_file = open(path,"r")
        deck_as_string = deck_file.read()
        deck = self.convert_string_to_deck(deck_import_name.value,deck_as_string)
        if(not(self.is_included(deck_import_name)) and self.is_deck_length_allowed()):
            self.decks.append(deck)
        deck_file.close()

    def export_deck(self,deck: Deck):
        if (not(self.is_file_exist(deck.name,EXPORTED_DECKS_PATH)) and (self.is_exporting_allowed(EXPORTED_DECKS_PATH)) ):
            deck_file = open(EXPORTED_DECKS_PATH + f"{deck.name}.txt","w")
            for card in deck.cards:
                deck_file.write(card.front + " " +card.back)
                deck_file.write("\n")
            deck_file.close()           

    def is_file_exist(self,file_name:str,directory:str) -> bool:
        return os.path.exists(directory + '/' + file_name + '.txt')

    def delete_deck(self,deck_name :str):
        if(self.is_included(deck_name)):
            self.decks.remove(self.fetch_deck(deck_name))

    def convert_string_to_deck(self, deck_name: str, deck_as_string: str) -> Deck:
        split_deck = deck_as_string.splitlines('\n')
        deck: Deck = Deck(deck_name)
        if(not(self.is_included(deck_name))):
            for line in split_deck:
                line = line.split(" ")
                deck.add_card(Card(line[0],line[1]))
            return deck
    
    def reset_exported_decks(self):
        for file in os.scandir(EXPORTED_DECKS_PATH):
            if file.is_file():
                os.remove(file)

    def set_current_deck(self,deck: Deck):
        self.current_deck = deck
    
    def reset_decks(self):
        self.reset_exported_decks()
        self.decks = [Deck(DeckNames.DECK_NAME_1.value)]
        self.current_index = 0
        self.update_current_deck()

    def default_decks(self):
        
        card_1 = Card("Front side", "Back side")
        card_2 = Card("This is a question", "This is the answer")
        deck_1 = Deck("Cool deck")
        deck_1.add_card(card_1)        
        deck_1.add_card(card_2)
        
        deck_2 = Deck(DeckNames.DECK_NAME_1.value)
        card_3 = Card("This is the", "First card in the deck")
        deck_2.add_card(card_3)

        self.decks = [deck_1,deck_2]
        self.update_current_deck()

    def update_current_deck(self):
        self.current_deck = self.decks[self.current_index]

    def set_current_index(self,index: int):
        self.current_index = index