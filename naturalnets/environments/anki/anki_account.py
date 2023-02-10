class AnkiAccount:
    """
    Anki Account is composed of username and password and used at anki login page
    """
    def __init__(self, account_name: str, account_password: str):
        self.account_name = account_name
        self.account_password = account_password
