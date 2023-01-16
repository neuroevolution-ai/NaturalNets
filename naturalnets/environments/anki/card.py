class Card():

    def __init__(self,front: str,back: str):
        self.front = front
        self.back = back
        self.tag = None

    def is_front_edited(self) -> bool:
        return "edited" in self.front

    def is_back_edited(self) -> bool:
        return "edited" in self.back
    
    def is_tag_edited(self) -> bool:
        return "edited" in self.tag

    def edit_front(self) -> None:
        if (not(self.is_front_edited())):
            self.front += " edited"

    def edit_back(self) -> None:
        if (not(self.is_back_edited())):
            self.back += " edited"

    def edit_tag(self) -> None:
        if (not(self.is_tag_edited())):
            self.tag = "edited"