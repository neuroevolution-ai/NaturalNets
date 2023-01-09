from pages.main_page import MainPage
from pages.profile_page import ProfilePage
class AppController:
    def __init__(self):
        self.main_window = MainPage()
        self.profile_page = ProfilePage()
