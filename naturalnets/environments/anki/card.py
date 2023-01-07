class Card():
    """
    I implement a card simply as a tuple (question,answer). Tag is regarding the logic irrelevant but is alterable
    and rewarded.
    """
    def __init__(self,front: str,back: str):
        self.front = front
        self.back = back
        self.tag = None

    def is_edited(self,card_component: str):
        return "edited" in card_component
    
    def edit_front(self):
        if (self.is_edited(self.front)):
            print("Front side is already edited")
            return
        else:
            self.front += " edited"

    def edit_back(self):
        if (self.is_edited(self.back)):
            print("Back side is already edited")
            return
        else:
            self.back += " edited"

    def edit_tag(self):
        if (self.is_edited(self.tag)):
            print("Tag is already edited")
            return
        else:
            self.tag = "edited"