from naturalnets.environments.anki.constants import FlagColour

class Card():
    """
    Difference between a card and a note
    https://tools2study.com/en/learn/anki-cards-vs-notes/#:~:text=Notes%20are%20a%20collection%20of,be%20created%20from%20one%20note.
    Notes are a collection of related information structured in different fields (e.g. Front, Back, Image). 
    Cards are a pair of an answer and a question based on the fields of the corresponding note.
    Thus, multiple cards can be created from one note.

    Since there will be no images etc. in my self-defined decks I am going to use the same implementation for both of the functionalities
    """
    def __init__(self,front: str,back: str,tags: str):
        self.front = front
        self.back = back
        self.tags = tags
        self.due_date = 1
        self.is_marked = False
        self.is_buried = False
        self.is_suspended = False
        self.flag_colour: FlagColour = None

    def mark_card(self):
        self.is_marked = True
    
    def demark_card(self):
        self.is_marked = False

    def bury_card(self):
        self.is_buried = True
    
    def debury_card(self):
        self.is_buried = False

    def suspend_card(self):
        self.is_suspended = True
    
    def desuspend_card(self):
        self.is_suspended = False
    
    def set_flag_colour(self,flag_colour: FlagColour):
        self.flag_colour = flag_colour
    
    def remove_flag_colour(self):
        self.flag_colour = None
    
    def decrement_due_date(self):
        if self.due_date != 0:
            self.due_date -= 1

    def increment_due_date(self):
        self.due_date += 1
    