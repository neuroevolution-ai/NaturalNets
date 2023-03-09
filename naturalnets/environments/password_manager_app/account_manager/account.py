
from typing import Optional


class Account:

    account_name: str
    user_id: str
    password: str
    url: str
    notes: str

    def __init__(self, account_name: str, user_id: Optional[str], password: Optional[str], url: Optional[str], notes: Optional[str]) -> None:
        self.account_name = account_name
        self.user_id = user_id
        self.password = password
        self.url = url
        self.notes = notes

    def __eq__(self, __o: object) -> bool:
        if type(__o) is Account:
            True if __o.account_name == self.account_name else False
        else:
            return False

    def get_account_name(self) -> str:
        return self.account_name
    
    def get_user_id(self) -> str:
        return self.user_id
    
    def get_password(self) -> str:
        return self.password
    
    def get_url(self) -> str:
        return self.url
    
    def get_notes(self) -> str:
        return self.notes
    

    def set_account_name(self, account_name: str) -> None:
        self.account_name = account_name
    
    def set_user_id(self, user_id: str) -> None:
        self.user_id = user_id
    
    def set_password(self, password: str) -> None:
        self.password = password
    
    def set_url(self, url: str) -> None:
        self.url = url
    
    def set_notes(self, notes: str) -> None:
        self.notes = notes
