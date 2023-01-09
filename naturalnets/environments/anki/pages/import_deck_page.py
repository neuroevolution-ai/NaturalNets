import os

import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH,PREDEFINED_DECKS_PATH
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki.deck import DeckDatabase

class ImportDeckPage(Page,RewardElement):
    """
    STATE_LEN is composed of if this window is open or not and the max number of predefined importable decks by 3
    """
    STATE_LEN = 4
    IMG_PATH = os.path.join(IMAGES_PATH, "import_deck.png")

    WINDOW_BB = BoundingBox(0, 0, 499, 412)
    CHOOSE_BB = BoundingBox(190, 371, 91, 27)
    HELP_BB = BoundingBox(394, 371, 91, 27)
    CLOSE_WINDOW_BB = BoundingBox(459, 0, 40, 38)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ImportDeckPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.current_index: int = 0

        self.choose_button: Button = Button(self.CHOOSE_BB, self.close())
        self.help_button: Button = Button(self.HELP_BB, self.help())
        self.close_window_button: Button = Button(self.CLOSE_WINDOW_BB, self.close())

    def handle_click(self,click_position: np.ndarray):
        if(self.choose_button.is_clicked_by(click_position)):
            self.choose_button.handle_click(click_position)
        elif(self.help_button.is_clicked_by(click_position)):
            self.help_button.is_clicked_by(click_position)
        elif(self.close_window_button.is_clicked_by(click_position)):
            self.close_window_button.is_clicked_by(click_position)
            
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])
    
    def help(self):
        print("Led to external website")
        self.register_selected_reward(["help","clicked"])
    
    def is_open(self) -> int:
        return self.get_state()[0]

    def change_current_deck_index(self,click_point: np.ndarray):
        # Items have size (469,22)
        # Box containing the items has size (472,110)
        # Top left corner (15,82)
        current_bounding_box = self.calculate_current_bounding_box()
        if(not(current_bounding_box.is_point_inside(click_point))):
            print("Point not inside the profiles bounding box")
            return
        else:
            click_index: int = click_point[1]/22
            self.current_index = click_index

    def calculate_current_bounding_box(self):
       upper_left_point = (15,82)
       length = 22 * DeckDatabase().count_number_of_files(PREDEFINED_DECKS_PATH)
       current_bounding_box = BoundingBox(upper_left_point[0], upper_left_point[1], 469, length)
       return current_bounding_box
    
    