import os
import numpy as np
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.anki.constants import IMAGES_PATH

class AboutPage(Page,RewardElement):
    """
    STATE_LEN specifies whether this window is open or not
    """
    STATE_LEN = 1
    WINDOW_BB = BoundingBox(0, 0, 1002, 869)
    OK_BUTTON_BB = BoundingBox(797, 840, 91, 24)
    COPY_DEBUG_INFO_BUTTON_BB = BoundingBox(898, 840, 101, 26)
    EXIT_BUTTON_BB = BoundingBox(960, 0, 42, 37)

    IMG_PATH = os.path.join(IMAGES_PATH, "about_page.png")

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AboutPage, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.copy_debug_info_button: Button = Button(self.COPY_DEBUG_INFO_BUTTON_BB, self.debug_info())
        self.ok_button: Button = Button(self.OK_BUTTON_BB, self.close())
        self.exit_button: Button = Button(self.EXIT_BUTTON_BB, self.close())
        self.add_widgets([self.ok_button,self.exit_button])

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],
            "copy_debug_info": "copied"
        }

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.ok_button.is_clicked_by(click_position):
            self.ok_button.handle_click(click_position)
        elif self.exit_button.is_clicked_by(click_position):
            self.exit_button.handle_click(click_position)
        elif self.copy_debug_info_button.is_clicked_by(click_position):
            self.copy_debug_info_button.handle_click(click_position)

    def debug_info(self):
        print("Copy debug info to the clipboard")
        self.register_selected_reward(["copy_debug_info","copied"])

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])

    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def is_open(self):
        return self.get_state()[0]