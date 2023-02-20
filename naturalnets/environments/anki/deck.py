import codecs
from typing import List

from naturalnets.environments.anki.card import Card
from naturalnets.environments.anki.constants import (DeckNames, DeckImportName, PREDEFINED_DECKS_PATH,
    EXPORTED_DECKS_PATH)
import os


class Deck:

    """
    A deck is composed of a name, cards, the current study index which implies the card,
    at which the profile is currently is and if the answer is currently shown
    """
    def __init__(self, deck_name: str):
        self.name = deck_name
        self.cards: List[Card] = []
        self.study_index: int = 0
        self.is_answer_shown = False

    """
    Proceed to the next card. If the user is at the end of the deck then go back to the first card
    """
    def increment_study_index(self):
        self.study_index += 1
        if self.study_index == len(self.cards):
            self.study_index = 0

    """
    Add a card to the deck
    """
    def add_card(self, card: Card):
        self.cards.append(card)

    """
    Return the length of the deck
    """
    def deck_length(self):
        return len(self.cards)

    """
    Remove a card from the deck and if the card was the last card of the deck decrement the study index
    and prevent index out of bound
    """
    def remove_card(self):
        self.cards.remove(self.cards[self.study_index])
        if self.study_index == self.deck_length():
            self.study_index -= 1


class DeckDatabase:

    """
    This class holds the currently selected decks, up to a maximum of 5
    """
    def __init__(self):

        # The names which a deck can get
        self.deck_names = [DeckNames.DECK_NAME_1.value, DeckNames.DECK_NAME_2.value, DeckNames.DECK_NAME_3.value,
                           DeckNames.DECK_NAME_4.value, DeckNames.DECK_NAME_5.value]
        # The names of predefined decks
        self.deck_import_names = [DeckImportName.DUTCH_NUMBERS.value, DeckImportName.GERMAN_NUMBERS.value,
                                  DeckImportName.ITALIAN_NUMBERS.value]
        # Current decks
        self.decks: List[Deck] = [Deck(DeckNames.DECK_NAME_1.value), Deck(DeckNames.DECK_NAME_2.value),
                                  Deck(DeckNames.DECK_NAME_3.value)]
        # Index of the currently selected deck
        self.current_index: int = 0

    """
    Return the number of decks
    """
    def decks_length(self) -> int:
        return len(self.decks)

    """
    Return true if the number of decks is less than 5.
    """
    def is_deck_length_allowed(self) -> int:
        return self.decks_length() < 5

    """
    Fetch a deck with deck_name if it is present
    """
    def fetch_deck(self, deck_name: str) -> Deck:
        for deck in self.decks:
            if deck_name == deck.name:
                return deck

    """
    Returns true if a deck with deck_name is present
    """
    def is_included(self, deck_name: str) -> bool:
        return self.fetch_deck(deck_name) is not None

    """
    Creates an empty deck with deck_name
    """
    def create_deck(self, deck_name: str):
        self.decks.append(Deck(deck_name))

    """
    Import the deck with name deck_import_name from the predefined decks path
    """
    def import_deck(self, deck_import_name: str) -> None:
        path = os.path.join(PREDEFINED_DECKS_PATH, deck_import_name + ".txt")
        deck_file = codecs.open(path, "r", encoding='utf-8')
        deck_as_string = deck_file.read()
        deck = self.convert_string_to_deck(deck_import_name, deck_as_string)
        if not (self.is_included(deck_import_name)) and self.is_deck_length_allowed():
            self.decks.append(deck)
        deck_file.close()

    """
    Delete deck with name deck_name if it is present
    """
    def delete_deck(self, deck_name: str) -> None:
        if self.is_included(deck_name):
            self.current_index = 0
            self.decks.remove(self.fetch_deck(deck_name))

    """
    Takes a string deck_as_string and converts it to a deck called deck_name
    """
    def convert_string_to_deck(self, deck_name: str, deck_as_string: str) -> Deck:
        split_deck = deck_as_string.splitlines(False)
        deck: Deck = Deck(deck_name)
        if not (self.is_included(deck_name)):
            for line in split_deck:
                if '\t' in line:
                    line = line.split('\t')
                    deck.add_card(Card(line[0], line[1]))
                elif ' ' in line:
                    line = line.split(' ')
                    deck.add_card(Card(line[0], line[1]))
        return deck

    """
    Reset the decks configuration to the configuration of only one deck 
    """
    def reset_decks(self) -> None:
        DeckDatabase.reset_exported_decks()
        self.decks = [Deck(DeckNames.DECK_NAME_1.value)]
        self.current_index: int = 0

    """
    This method is called when the application status is reset
    """
    def default_decks(self) -> None:
        card_1 = Card("Front side", "Back side")
        card_2 = Card("This is a question", "This is the answer")
        deck_1 = Deck("Cool deck")

        deck_1.add_card(card_1)
        deck_1.add_card(card_2)

        deck_2 = Deck(DeckNames.DECK_NAME_1.value)
        card_3 = Card("This is the", "First card in the deck")
        deck_2.add_card(card_3)

        self.decks = [deck_1, deck_2]

    """
    Changes the index of the current deck with index
    """
    def set_current_index(self, index: int) -> None:
        self.current_index = index

    """
    Provides the number of the files within a directory. It is used for importing and exporting decks.
    """
    @staticmethod
    def count_number_of_files(dir_path: str) -> int:
        count = 0
        for path in os.scandir(dir_path):
            if path.is_file():
                count += 1
        return count

    """
    Deletes all of the files in the exported decks directory
    """
    @staticmethod
    def reset_exported_decks() -> None:
        for file in os.scandir(EXPORTED_DECKS_PATH):
            if file.is_file():
                os.remove(file)

    """
    Returns true if directory has a .txt file of file_name
    """
    @staticmethod
    def is_file_exist(file_name: str, directory: str) -> bool:
        return os.path.exists(directory + '/' + file_name + '.txt')

    """
    Returns true if number of files in exported decks path is less than 5
    """
    @staticmethod
    def is_exporting_allowed() -> bool:
        return DeckDatabase.count_number_of_files(EXPORTED_DECKS_PATH) < 5

    """
    Converts a deck to a .txt file
    """
    @staticmethod
    def export_deck(deck: Deck) -> None:
        if not (DeckDatabase.is_file_exist(deck.name, EXPORTED_DECKS_PATH)) and (DeckDatabase.is_exporting_allowed()):
            print(EXPORTED_DECKS_PATH)
            deck_file = codecs.open(os.path.join(EXPORTED_DECKS_PATH, f"{deck.name}.txt"), "w", encoding='utf-8')
            for card in deck.cards:
                deck_file.write(card.front + " " + card.back)
                deck_file.write("\n")
            deck_file.close()
