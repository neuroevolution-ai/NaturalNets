import os
import numpy as np
from naturalnets.environments.anki.pages.main_page_popups import AddDeckPopupPage
from naturalnets.environments.anki import DeckDatabase
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.utils import put_text
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.widgets.button import Button

class ChooseDeckPage(Page,RewardElement):
    """
        State description:
            state[0]: if this window is open
            state[i]: i-th menu item of the profiles bounding-box (6 > i > 0)
    """
    STATE_LEN = 6
    IMG_PATH = os.path.join(IMAGES_PATH, "choose_deck.png")

    WINDOW_BB = BoundingBox(20, 20, 498, 375)
    CHOOSE_BB = BoundingBox(210, 355, 91, 27)
    ADD_BB = BoundingBox(311, 355, 91, 27)
    HELP_BB = BoundingBox(413, 355, 91, 27)

    DECK_BB = BoundingBox(33, 65, 472, 280)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ChooseDeckPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.add_deck_popup = AddDeckPopupPage()
        self.add_child(self.add_deck_popup)

        self.current_index: int = 0

        self.add_button: Button = Button(self.ADD_BB, self.add_deck_popup.open)
        self.choose_button: Button = Button(self.CHOOSE_BB, self.choose_deck)
        self.help_button: Button = Button(self.HELP_BB, self.help)

        self.add_widgets([self.add_button, self.choose_button, self.help_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "index": [0, 1, 2, 3, 4],
            "help": 0,
        }
    
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

    def change_current_deck_index(self,click_point:np.ndarray):
        # Items have size (469,22)
        # Box containing the items has size (472,280)
        # Top left corner (33,65)
        current_bounding_box = self.calculate_current_bounding_box()
        if((current_bounding_box.is_point_inside(click_point))):
            click_index: int = (click_point[1] - 65)/22
            self.current_index = click_index
            self.register_selected_reward(["index", self.current_index])

    def calculate_current_bounding_box(self):
       upper_left_point = (33,65)
       length = 22 * DeckDatabase().decks_length()
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 472, length)
       return current_bounding_box

    def choose_deck(self):
        DeckDatabase().set_current_index(self.current_index)
        DeckDatabase().set_current_deck(DeckDatabase().decks[self.current_index])
        self.register_selected_reward(["index", f"{self.current_index}"])
        for i in range(1,6):
            self.get_state()[i] = 0
        self.get_state()[self.current_index + 1] = 1

    def reset_index(self):
        self.current_index = 0
    
    def render(self,img: np.ndarray):
        img = super().render(img)
        # Items have size (469,22)
        for i, deck in enumerate (DeckDatabase().decks):
            put_text(img, f" {deck.name}", (36, 65 + 22 * (i + 1)), font_scale = 0.3)
        return img

    def handle_click(self, click_position: np.ndarray) -> None:
        "return super().handle_click(click_position)"