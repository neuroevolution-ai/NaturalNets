import os
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown,DropdownItem
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.anki import DeckDatabase


class ExportDeckPage(Page,RewardElement):
    
    """
    State description:
            state[0]: if this window is open
            state[1]: if the dropdown is open 
    """
    
    STATE_LEN = 2
    IMG_PATH = os.path.join(IMAGES_PATH, "export_deck_page.png")
    
    WINDOW_BB = BoundingBox(100, 100, 380, 278)
    INCLUDE_DD_BB = BoundingBox(246, 145, 222, 24)
    HTML_CHECKBOX_BB = BoundingBox(113, 179, 16, 16)
    EXPORT_BB = BoundingBox(272, 339, 91, 26)
    CANCEL_BB = BoundingBox(374, 338, 91, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ExportDeckPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        dropdown_items = []
        for deck in DeckDatabase().decks:
            dropdown_items.append(DropdownItem(deck,deck.name))

        self.include_dropdown = Dropdown(self.INCLUDE_DD_BB, dropdown_items)
        self.html_checkbox = CheckBox(self.HTML_CHECKBOX_BB, None)
        self.export_button = Button(self.EXPORT_BB, self.export_deck)
        self.cancel_button = Button(self.CANCEL_BB, self.close)

        self.add_widgets([self.include_dropdown, self.html_checkbox,
            self.export_button, self.cancel_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "checkbox": [True, False],
            "exported": 0
        }
 
    def handle_click(self,click_position: np.ndarray):
        if (self.include_dropdown.is_open()):
            self.include_dropdown.handle_click(click_position)
            self.get_state()[1] = not(self.get_state()[1])
        
        if (not(self.include_dropdown.is_open())):
            if(self.html_checkbox.is_clicked_by(click_position)):
                self.html_checkbox.handle_click(click_position)
            elif(self.export_button.is_clicked_by(click_position)):
                self.export_button.handle_click(click_position)
            elif(self.cancel_button.is_clicked_by(click_position)):
                self.cancel_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])

    def is_open(self):
        return self.get_state()[0]

    def reset_current_deck(self):
        self.include_dropdown.set_selected_item(self.include_dropdown.get_all_items()[0])

    def export_deck(self):
        self.register_selected_reward(["exported"])
        DeckDatabase().export_deck(self.include_dropdown.get_selected_item().get_value())

    def render(self,img:np.ndarray):
        img = super().render(img)
        if (self.get_state()[1] == 1):
            self.include_dropdown.render(img)
        return img