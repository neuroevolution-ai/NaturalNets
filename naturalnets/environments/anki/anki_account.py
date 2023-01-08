from pages.anki_login_page import AnkiLoginPage
class AnkiAccount():

    def __init__(self,account_name: str,account_password: str):
        self.account_name = account_name
        self.account_password = account_password


class AnkiAccountDatabase():

    def __init__(self):
        self.active_account: AnkiAccount = None
        self.anki_username_list = ["account_1","account_2","account_3","account_4","account_5"]
        self.anki_password_list = ["pTgHAa","L7WwEH","yfTVwA","DP7xg7","zx7FeR"]

    def login(self):
        if(not(AnkiLoginPage().username_clipboard is not None 
            and AnkiLoginPage().password_clipboard is not None)):
            print("Username or password is not set")
        else:
            self.active_account = AnkiAccount(AnkiLoginPage().username_clipboard,AnkiLoginPage().password_clipboard)