class Card():
    """
    I implement a card simply as a tuple (question,answer). Tag is regarding the logic irrelevant but is alterable
    and rewarded.
    """
    def __init__(self,front: str,back: str):
        self.front = front
        self.back = back
        self.tag = None

    def is_front_edited(self):
        return "edited" in self.front

    def is_back_edited(self):
        return "edited" in self.back
    
    def is_tag_edited(self):
        return "edited" in self.tag

    def edit_front(self):
        if (not(self.is_front_edited())):
            self.front += " edited"

    def edit_back(self):
        if (not(self.is_back_edited())):
            self.back += " edited"

    def edit_tag(self):
        if (not(self.is_tag_edited())):
            self.tag = "edited"