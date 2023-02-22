class Card:
    """
    A card is composed of front-, and backside and an optional tag
    """

    def __init__(self, front: str, back: str, tag: str):
        self.front = front
        self.back = back
        self.tag = tag
    
    def get_front(self):
        return self.front
    
    def get_back(self):
        return self.back
    
    def get_tag(self):
        return self.tag

    """
    Check if the front side includes substring "edited"
    """
    def is_front_edited(self) -> bool:
        return "edited" in self.front

    """
    Check if the back side includes substring "edited"
    """
    def is_back_edited(self) -> bool:
        return "edited" in self.back

    """
    Check if the tag includes substring "edited"
    """
    def is_tag_edited(self) -> bool:
        if self.tag is not None:
            return "edited" in self.tag

    """
    Append " edited" to the front side string
    """
    def edit_front(self) -> None:
        if not (self.is_front_edited()):
            self.front += " edited"

    """
    Append " edited" to the back side string
    """
    def edit_back(self) -> None:
        if not (self.is_back_edited()):
            self.back += " edited"

    """
    Append " edited" to the tag string
    """
    def edit_tag(self) -> None:
        if self.tag is None:
            self.tag = ""
        if not (self.is_tag_edited()):
            self.tag += " edited"
