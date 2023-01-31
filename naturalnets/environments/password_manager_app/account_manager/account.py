
class Account:

    account_name: str
    user_id: str
    password: str
    url: str
    notes: str

    def __init__(self, account_name: str, user_id: str, password: str, url: str, notes: str) -> None:
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

    def getAccountName(self) -> str:
        return self.account_name
    
    def getUserId(self) -> str:
        return self.user_id
    
    def getPassword(self) -> str:
        return self.password
    
    def getUrl(self) -> str:
        return self.url
    
    def getNotes(self) -> str:
        return self.notes
    

    def setAccountName(self, account_name: str) -> None:
        self.account_name = account_name
    
    def setUserId(self, user_id: str) -> None:
        self.user_id = user_id
    
    def setPassword(self, password: str) -> None:
        self.password = password
    
    def setUrl(self, url: str) -> None:
        self.url = url
    
    def setNotes(self, notes: str) -> None:
        self.notes = notes
