import codecs
from typing import List

from naturalnets.environments.anki import Card
from naturalnets.environments.anki.constants import DeckNames,DeckImportName,PREDEFINED_DECKS_PATH,EXPORTED_DECKS_PATH
import os

class Deck():
    
    def __init__(self,deck_name:str):
        self.name = deck_name
        self.cards: List[Card] = []
        self.study_index: int = 0
        self.is_answer_shown = False
        
    def increment_study_index(self):
        if(self.study_index < len(self.cards) - 1):
            self.study_index += 1 
        elif(self.study_index == len(self.cards)):
            self.study_index = len(self.cards) - 1
        else:
            self.study_index = 0
    
    def add_card(self,card: Card):
        self.cards.append(card)
    
    def deck_length(self):
        return len(self.cards)
    
    def remove_card(self):
        self.cards.remove(self.cards[self.study_index])
        if(self.study_index == self.deck_length()):
            self.study_index -= 1

class DeckDatabase():

    #
    # Restrict the max number of decks and exported files by 5
    # 

    def __init__(self):
        
        self.deck_names = [DeckNames.DECK_NAME_1.value, DeckNames.DECK_NAME_2.value, DeckNames.DECK_NAME_3.value, DeckNames.DECK_NAME_4.value, DeckNames.DECK_NAME_5.value]
        self.deck_import_names = [DeckImportName.DUTCH_NUMBERS.value, DeckImportName.GERMAN_NUMBERS.value, DeckImportName.ITALIAN_NUMBERS.value]
        self.decks: List[Deck] = [Deck(DeckNames.DECK_NAME_1.value),Deck(DeckNames.DECK_NAME_2.value),Deck(DeckNames.DECK_NAME_3.value)]
        self.current_index: int = 0

    def decks_length(self) -> int:
        return len(self.decks)

    def is_deck_length_allowed(self) -> int:
        return self.decks_length() < 5

    def count_number_of_files(self,dir_path: str) -> int:
        count = 0
        for path in os.scandir(dir_path):
            if path.is_file():
                count += 1
        return count 
    
    def is_exporting_allowed(self) -> bool:
        return self.count_number_of_files(EXPORTED_DECKS_PATH) < 5

    def fetch_deck(self,deck_name: str) -> Deck:
        for deck in self.decks:
            if(deck_name == deck.name):
                return deck
        return None

    def is_included(self,deck_name: str) -> bool:
        return self.fetch_deck(deck_name) is not None
    
    def create_deck(self,deck_name:str) -> bool:
        self.decks.append(Deck(deck_name))
    
    def import_deck(self,deck_import_name: str) -> None:
        path = os.path.join(PREDEFINED_DECKS_PATH, deck_import_name + ".txt")
        deck_file = codecs.open(path,"r",encoding='utf-8')
        deck_as_string = deck_file.read()
        deck = self.convert_string_to_deck(deck_import_name,deck_as_string)
        if(not(self.is_included(deck_import_name)) and self.is_deck_length_allowed()):
            self.decks.append(deck)
        deck_file.close()

    def export_deck(self,deck: Deck) -> None:
        if (not(self.is_file_exist(deck.name,EXPORTED_DECKS_PATH)) and (self.is_exporting_allowed()) ):
            deck_file = codecs.open(EXPORTED_DECKS_PATH + f"{deck.name}.txt","w",encoding='utf-8')
            for card in deck.cards:
                deck_file.write(card.front + " " +card.back)
                deck_file.write("\n")
            deck_file.close()           

    def is_file_exist(self,file_name:str,directory:str) -> bool:
        return os.path.exists(directory + '/' + file_name + '.txt')

    def delete_deck(self,deck_name :str) -> None:
        if(self.is_included(deck_name)):
            self.current_index = 0
            self.decks.remove(self.fetch_deck(deck_name))

    
    def convert_string_to_deck(self, deck_name: str, deck_as_string: str) -> Deck:
        split_deck = deck_as_string.splitlines(False)
        deck: Deck = Deck(deck_name)
        if(not(self.is_included(deck_name))):
            for line in split_deck:
                if ('\t' in line):
                    line = line.split('\t')
                    deck.add_card(Card(line[0],line[1]))
                elif(' ' in line):
                    line = line.split(' ')
                    deck.add_card(Card(line[0],line[1]))
        return deck
        
    
    def reset_exported_decks(self) -> None:
        for file in os.scandir(EXPORTED_DECKS_PATH):
            if file.is_file():
                os.remove(file)
    
    def reset_decks(self) -> None:
        self.reset_exported_decks()
        self.decks = [Deck(DeckNames.DECK_NAME_1.value)]
        self.current_index: int = 0

    def default_decks(self) -> None:
        card_1 = Card("Front side", "Back side")
        card_2 = Card("This is a question", "This is the answer")
        deck_1 = Deck("Cool deck")
        
        deck_1.add_card(card_1)
        deck_1.add_card(card_2)
        
        deck_2 = Deck(DeckNames.DECK_NAME_1.value)
        card_3 = Card("This is the", "First card in the deck")
        deck_2.add_card(card_3)

        self.decks = [deck_1,deck_2]

    def set_current_index(self,index: int) -> None:
        self.current_index = index