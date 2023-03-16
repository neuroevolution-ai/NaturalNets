class AnkiAccount:
    """
    Anki Account is composed of username and password and used at anki login page
    """
    
    def __init__(self, account_name: str, account_password: str):
        self.account_name = account_name
        self.account_password = account_password

    def get_account_name(self):
        return self.account_name
    
    def get_account_password(self):
        return self.account_password
