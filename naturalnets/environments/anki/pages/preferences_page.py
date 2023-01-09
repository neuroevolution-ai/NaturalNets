from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement


class PreferencesPage(RewardElement,Page):
    ""

    def open(self):
        self.get_state()[0] = 1
    
    def close(self):
        self.get_state()[0] = 0
    
    def is_open(self):
        return self.get_state()[0]