import cv2
import numpy as np

from typing import Callable, List
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.colors import Color
from naturalnets.environments.app.page import Widget
from naturalnets.environments.app.utils import get_group_bounding_box

class DropdownItem(Widget):
    STATE_LEN = 1

    # BoundingBox is set by/depends on Dropdown
    def __init__(self, bounding_box:BoundingBox=BoundingBox(0,0,0,0), is_active_constraint:Callable=lambda: True):
        super().__init__(self.STATE_LEN, bounding_box)
        self._is_active = is_active_constraint

    def is_active(self) -> bool:
        return self._is_active()

    def handle_click(self, click_position: np.ndarray = None) -> None:
        #TODO
        pass

    def render(self, img: np.ndarray) -> np.ndarray:
        x, y, width, height = self.get_bb().get_as_tuple()
        start_point = (x,y)
        end_point = (x + width, y + height)
        color = Color.BLACK.value
        thickness = 2
        cv2.rectangle(img, start_point, end_point, color, thickness)
        return img

class Dropdown(Widget):
    INITIAL_STATE_LEN = 1

    def __init__(self, bounding_box:BoundingBox, items:List[DropdownItem]):
        super().__init__(self.INITIAL_STATE_LEN, bounding_box)
        self.dropdown_button_bb = bounding_box
        self._all_items:list[DropdownItem] = items 
        self.add_children(self._all_items)
        
    def is_open(self):
        return self.get_state()[0]
        
    def open(self):
        """Opens the dropdown, if it contains at least one item.
        """
        if len(self.get_items()) > 0:
            self.get_state()[0] = 1

    def close(self):
        self.get_state()[0] = 0

    def handle_click(self, click_position: np.ndarray = None) -> None:
        if self.is_open():
            for item in self.get_items():
                if item.is_clicked_by(click_position):
                    item.handle_click(click_position)
            # any click action closes dropdown if it was open
            self.close()
        else:
            self.open()

    #override
    def get_bb(self):
        if not self.is_open():
            return self.dropdown_button_bb
        else:
            return get_group_bounding_box(self.get_items())

    def get_items(self):
        i:int = 0
        first_bb = self.dropdown_button_bb
        available_items:list[DropdownItem] = []
        for item in self._all_items:
            #TODO: check if window bounds are surpassed by any item's next_bb
            next_bb = BoundingBox(first_bb.x, first_bb.y + first_bb.height*i, first_bb.width, first_bb.height)
            if item.is_active():
                item.set_bb(next_bb)
                available_items.append(item)
                i += 1
        return available_items
    
    def render(self, img: np.ndarray) -> np.ndarray:
        if self.is_open():
            for item in self.get_items():
                item.render(img)
        else:
            #TODO
            pass
        return img

  