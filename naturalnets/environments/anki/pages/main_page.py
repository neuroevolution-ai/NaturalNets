import os
from choose_deck_study_page import ChooseDeckStudyPage
from anki.pages.check_media_page import CheckMediaPage
from pages.export_page import ExportPage
from pages.import_page import ImportPage
from profile_page import ProfilePage
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.anki_account import AnkiAccountDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem

anki_account_database = AnkiAccountDatabase()

class MainPage(Page,RewardElement):
    
    STATE_LEN = 9
    IMG_PATH = os.path.join(IMAGES_PATH, "main_page.png")

    WINDOW_BB = BoundingBox(0, 0, 831, 750)
    DECKS_BB = BoundingBox(194, 155, 458, 150)
    
    GET_SHARED_BB = BoundingBox(272, 700, 93, 27)
    CREATE_DECK_BB = BoundingBox(369, 700, 93, 27)
    IMPORT_FILE_BB = BoundingBox(473, 700, 93, 27)
    
    DECKS_BB = BoundingBox(236, 68, 56, 29)
    ADD_BB = BoundingBox(310, 68, 46, 29)
    SYNC_BB = BoundingBox(524, 68, 54, 29)
    
    FILE_DROPDOWN_BB = BoundingBox(0, 41, 43, 23)
    EDIT_DROPDOWN_BB = BoundingBox(43, 41, 47, 23)
    TOOLS_DROPDOWN_BB = BoundingBox(90, 41, 53, 23)
    HELP_DROPDOWN_BB = BoundingBox(143, 41, 50, 23)
    CLOSE_WINDOW_BB = BoundingBox(777, 0, 54, 34)


    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MainPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.profile_page = ProfilePage()
        self.import_page = ImportPage()
        self.export_page = ExportPage()
        self.choose_deck_study_page = ChooseDeckStudyPage()
        self = CheckMediaPage()

        switch_profile_ddi = DropdownItem(self.switch_profile(), "Switch Profile")
        import_ddi = DropdownItem(self.import_page.open(), "Import")
        export_ddi = DropdownItem(self.export_page.open(), "Export")
        exit_ddi = DropdownItem(self.exit_app(), "Exit")

        study_deck_ddi = DropdownItem(self.choose_deck_study_page.open(), "Study Deck")
        check_media_ddi = DropdownItem(self)

        file_dropdown = Dropdown(self.FILE_DROPDOWN_BB,[switch_profile_ddi,import_ddi,export_ddi,exit_ddi])
        edit_dropdown = Dropdown(self.EDIT_DROPDOWN_BB,[])
        tools_dropdown = Dropdown(self.TOOLS_DROPDOWN_BB,[])

    def open(self):
        self.get_state()[0] = 1
    
    def close(self):
        self.get_state()[0] = 0
    
    def is_open(self):
        return self.get_state()[0]

    def switch_profile(self):
        self.close()
        self.profile_page.open()

    def exit_app(self):
        self.profile_page.open()
        self.profile_page.reset_all()
        self.close()
