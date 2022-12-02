from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.passlock_app.main_window_pages.auto_page import AutoPage
from naturalnets.environments.passlock_app.main_window_pages.manual_page import ManualPage
from naturalnets.environments.passlock_app.main_window_pages.search_page import SearchPage
from naturalnets.environments.passlock_app.main_window_pages.settings_page import SettingsPage

class HomeWindow(StateElement, Clickable, RewardElement):
    """The main window of the app, containing the menu as well as the respective pages
    (manual page, auto page, search page and setting page).

       State description:
            state[i]: represents the selected/shown status of page i, i in {0,..,2}.
    """

    STATE_LEN = 4
    #IMG_PATH = os.path.join(IMAGES_PATH, "main_window_base.png")

    
    APP_BOUNDING_BOX = BoundingBox(0, 0, 1180, 850)

    HOME_BUTTON_BB = BoundingBox(9, 28, 99, 22)
    SEARCH_BUTTON_BB = BoundingBox(9, 56, 99, 22)
    SETTINGS_BUTTON_BB = BoundingBox(9, 84, 99, 22)
    SYNC_BUTTON_BB = BoundingBox(9, 112, 99, 22)
    DARK_LIGHT_BB = BoundingBox(9, 112, 99, 22)

    def __init__(self):
        StateElement.__init__(self, self.STATE_LEN)
        RewardElement.__init__(self)

        self._bounding_box = self.APP_BOUNDING_BOX

        self.manual = ManualPage()
        self.auto = AutoPage()
        self.search = SearchPage()
        self.settings = SettingsPage()
        
