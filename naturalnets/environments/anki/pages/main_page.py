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
