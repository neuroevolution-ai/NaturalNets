import random
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.anki_account import AnkiAccountDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox

anki_account_database = AnkiAccountDatabase()

class MainPage(Page,RewardElement):
    
    WINDOW_BB = BoundingBox(0, 0, 831, 750)


    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MainPage, cls).__new__(cls)
        return cls.instance

    anki_accounts = { anki_account_database.anki_accounts_list[0].account_name: anki_account_database.anki_accounts_list[0].account_password,
                      anki_account_database.anki_accounts_list[1].account_name: anki_account_database.anki_accounts_list[1].account_password,
                      anki_account_database.anki_accounts_list[2].account_name: anki_account_database.anki_accounts_list[2].account_password,
                      anki_account_database.anki_accounts_list[3].account_name: anki_account_database.anki_accounts_list[3].account_password,
                      anki_account_database.anki_accounts_list[4].account_name: anki_account_database.anki_accounts_list[4].account_password,                 
                    }
    def update_current_account(self):
        """
        In the original application this method requires interaction with the anki servers via internet browser.
        To make the application much easier and avoid distraction from the testing purposes I implement the following:
        Each click to "OK" button in the Anki window randomly chooses one of the pre-created account in the form of (username,password).
        Also the reward function may consider whether the account has ben chosen already.
        """
        anki_account_database.active_account = random.choice(anki_account_database.anki_accounts_list)

    def get_shared(self):
        """
        """
