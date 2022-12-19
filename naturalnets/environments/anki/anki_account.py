from typing import Final

class AnkiAccount():

    def __init__(self,account_name: str,account_password: str):
        self.account_name = account_name
        self.account_password = account_password


class AnkiAccountDatabase():

    def __init__(self):
        self.active_account: AnkiAccount = None
        self.anki_accounts_list: Final = [AnkiAccount("account_1","pTgHAa"),AnkiAccount("account_2","L7WwEH"),
        AnkiAccount("account_3","yfTVwA"),AnkiAccount("account_4","DP7xg7"),AnkiAccount("account_5","zx7FeR")]

    