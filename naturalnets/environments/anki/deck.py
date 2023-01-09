import string

import numpy as np
from naturalnets.environments.anki.card import Card
from naturalnets.environments.anki.constants import InsertionOrder,StandardSettingValues,LeechAction
from naturalnets.environments.anki.deck import Deck,DeckDatabase
from naturalnets.environments.anki.constants import OptionNames,DeckNames,DeckImportName,PREDEFINED_DECKS_PATH,EXPORTED_DECKS_PATH
import random
import os

from naturalnets.environments.gui_app.bounding_box import BoundingBox
class Deck():
    
    def __init__(self,name:str):
        
        self.secure_random = random.SystemRandom()
        self.name = name
        self.cards: list[Card] = []
        self.current_card: Card = None

    def is_front_side_clipboard(self):
        return self.front_side_clipboard_temporary_string is not None

    def is_back_side_clipboard(self):
        return self.back_side_clipboard_temporary_string is not None
    
    def is_tag_clipboard(self):
        return self.tag_clipboard_temporary_string is not None

    def set_front_side_clipboard(self):
        self.front_side_clipboard_temporary_string = self.secure_random.choices(string.ascii_lowercase + string.digits, 10)
    
    def set_back_side_clipboard(self):
        self.back_side_clipboard_temporary_string = self.secure_random.choices(string.ascii_lowercase + string.digits, 10)

    def set_tag_clipboard(self):
        self.tag_clipboard_temporary_string = self.secure_random.choices(string.ascii_lowercase + string.digits, 10)
    
    def add_card(self,card:Card):
        self.cards.append(card)

class DeckDatabase():

    #
    # Restrict the max number of decks and exported files by 5
    # 

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeckDatabase, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        
        self.secure_random = random.SystemRandom()
        self.deck_names = [DeckNames.DECK_NAME_1, DeckNames.DECK_NAME_2, DeckNames.DECK_NAME_3, DeckNames.DECK_NAME_4, DeckNames.DECK_NAME_5]
        self.deck_import_names = [DeckImportName.DUTCH_NUMBERS, DeckImportName.GERMAN_NUMBERS, DeckImportName.ITALIAN_NUMBERS]
        self.decks: list[Deck] = [Deck(DeckNames.DECK_NAME_1)]
        self.current_deck: Deck = Deck(DeckNames.DECK_NAME_1)
        self.current_index = 0

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

    def is_importing_allowed(self):
        return self.decks_length() < 5
    
    def is_exporting_allowed(self):
        return self.count_number_of_files(EXPORTED_DECKS_PATH) < 5

    def fetch_deck(self,deck_name: str) -> Deck:
        for deck in self.decks:
            if(deck_name == deck.name):
                return deck
        return None

    def is_included(self,deck_name: str):
        return self.fetch_deck(deck_name) is None
    
    def create_deck(self,deck_name:str):
        self.decks.append(Deck(deck_name))
    
    def import_deck(self,deck_import_name: DeckImportName):
        path = os.path.join(PREDEFINED_DECKS_PATH, deck_import_name.value + ".txt")
        deck_file = open(path,"r")
        deck_as_string = deck_file.read()
        deck = self.convert_string_to_deck(deck_import_name.value,deck_as_string)
        if(self.is_included(deck_import_name.value)):
            print("Deck already present")
            return
        elif (not(self.is_importing_allowed())):
            print("The number of decks cannot exceed 5")
        else:
            self.decks.append(deck)
        deck_file.close()

    def export_deck(self,deck: Deck):
        if (not(self.is_exporting_allowed(EXPORTED_DECKS_PATH))):
            print("Number of exported decks can not be more than 5")
            return
        elif (not(self.is_file_exist(deck.name,EXPORTED_DECKS_PATH))):
            deck_file = open(EXPORTED_DECKS_PATH + f"{deck.name}.txt","w")
            for card in deck.cards:
                deck_file.write(card.front + " " +card.back)
                deck_file.write("\n")
            deck_file.close()           
        else:
            print("File already exists")

    def is_file_exist(self,file_name:str,directory:str) -> bool:
        return os.path.exists(directory + '/' + file_name + '.txt')

    def delete_deck(self,deck_name :str):
        if(not(self.is_included(deck_name))):
            print("Deck is not present")
            return
        else:
            self.decks.remove(self.fetch_deck(deck_name))

    def convert_string_to_deck(self, deck_name: str, deck_as_string: str) -> Deck:
        split_deck = deck_as_string.splitlines('\n')
        deck: Deck = Deck(deck_name)
        if(self.is_included(deck_name)):
            print("Deck is already present")
            return
        for line in split_deck:
            line = line.split(" ")
            deck.add_card(Card(line[0],line[1]))
        return deck
    
    def reset_exported_decks(self):
        for file in os.scandir(EXPORTED_DECKS_PATH):
            if file.is_file():
                os.remove(file)
    
    def rename_deck(self,deck :Deck):
        if (self.current_field_string is None):
            print("Name is not specified")
        elif (self.is_included(self.current_field_string)):
            print("Deck name is already present")
        else:
            deck.name = self.current_field_string

    def set_current_deck(self,deck: Deck):
        self.current_deck = deck
    
    def reset_decks(self):
        self.reset_exported_decks()
        self.decks = [Deck(DeckNames.DECK_NAME_1)]
        self.current_index = 0
        self.current_deck = self.decks[0]

    def get_deck_names(self):
        deck_names = []
        for deck in self.decks:
            deck_names.append(deck.name)
        return deck_names