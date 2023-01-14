import os
import numpy as np
from import_deck_page import ImportDeckPage
from naturalnets.environments.anki.deck import Deck
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH,PREDEFINED_DECKS_PATH
from naturalnets.environments.gui_app.utils import put_text
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki.deck import DeckDatabase

class ImportDeckPopupPage(Page,RewardElement):
    """
    State description:
            state[0]: if this window is open
            state[i]: if the i-th item is selected i = {1,2,3}
    """
    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "import_deck_popup.png")

    WINDOW_BB = BoundingBox(100, 100, 499, 373)
    CHOOSE_BB = BoundingBox(290, 434, 91, 27)
    HELP_BB = BoundingBox(494, 434, 91, 27)
    DECK_BB = BoundingBox(113, 145, 472, 280)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ImportDeckPopupPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.current_index: int = 0

        self.choose_button: Button = Button(self.CHOOSE_BB, self.choose_deck())
        self.help_button: Button = Button(self.HELP_BB, self.help())
        self.add_widgets([self.choose_button, self.help_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2, 3, 4],
            "help": 0,
        }
    
    def handle_click(self,click_position: np.ndarray):
        if(self.choose_button.is_clicked_by(click_position)):
            self.choose_button.handle_click(click_position)
        elif(self.help_button.is_clicked_by(click_position)):
            self.help_button.handle_click(click_position)
            
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])
    
    def help(self):
        print("Led to external website")
        self.register_selected_reward(["help"])
    
    def is_open(self) -> int:
        return self.get_state()[0]

    def change_current_deck_index(self,click_point: np.ndarray):
        # Items have size (469,22)
        # Box containing the items has size (472,280)
        # Top left corner (13,45)
        current_bounding_box = self.calculate_current_bounding_box()
        if(current_bounding_box.is_point_inside(click_point)):
            click_index: int = (click_point[1] - 145)/22
            self.current_index = click_index
            self.register_selected_reward(["index", click_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (115,145)
       length = 22 * DeckDatabase().count_number_of_files(PREDEFINED_DECKS_PATH)
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 472, length)
       return current_bounding_box
    
    def choose_deck(self):
        ImportDeckPage().current_deck = Deck(DeckDatabase().deck_import_names[self.current_index])

    def render(self,img: np.ndarray):
        img = super().render(img)
        for i, deck_name in enumerate (DeckDatabase().deck_import_names):
            put_text(img, f"{deck_name}", (115, 145 + (22 * (i + 1))), font_scale = 0.3)
        return img