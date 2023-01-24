import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button

class CheckMediaPage(Page,RewardElement):
    
    """
    State description:
            state[0]: if this window is open
    """
    
    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "check_media_page.png")
    
    WINDOW_BB = BoundingBox(100, 100, 622, 499)
    CLOSE_BB = BoundingBox(616, 567, 78, 28)
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CheckMediaPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.IMG_PATH)
        RewardElement.__init__(self)
        
        self.close_button = Button(self.CLOSE_BB,self.close)

    @property
    def reward_template(self):
        return {
            "window": ["open", "close"]
        }

    def handle_click(self,click_position: np.ndarray):
        if self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    def close(self):
        self.register_selected_reward(["window", "close"])
        self.get_state()[0] = 0
        

    def is_open(self) -> int:
        return self.get_state()[0]

    def render(self,img: np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        return img
        