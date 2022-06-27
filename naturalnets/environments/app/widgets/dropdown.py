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
    def __init__(self, value, bounding_box:BoundingBox=BoundingBox(0,0,0,0)):
        super().__init__(self.STATE_LEN, bounding_box)
        self._is_visible = True
        self._value = value
        self.get_state()[0] = 0 # is_selected state
        
    def get_value(self):
        return self._value

    def is_visible(self) -> bool:
        return self._is_visible
        
    def _set_visible(self, active:bool) -> None:
        self._is_visible = active

    def handle_click(self, click_position: np.ndarray = None) -> None:
        #TODO: probably not needed
        pass

    def set_selected(self, selected:bool):
        self.get_state()[0] = selected

    def is_selected(self) -> bool:
        return self.get_state()[0]

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
        self._selected_item = None
        
    def is_open(self):
        return self.get_state()[0]
        
    def open(self):
        """Opens the dropdown, if it contains at least one item.
        """
        if len(self.get_visible_items()) > 0:
            self.get_state()[0] = 1

    def close(self):
        self.get_state()[0] = 0

    def handle_click(self, click_position: np.ndarray = None) -> None:
        if self.is_open():
            for item in self.get_visible_items():
                if item.is_clicked_by(click_position):
                    self.set_selected_item(item)
                    #item.handle_click(click_position)
            # any click action closes dropdown if it was open
            self.close()
        else:
            self.open()

    def set_visible(self, ddi:DropdownItem, visible:bool):
        index = self._all_items.index(ddi)
        item = self._all_items[index]
        item._set_visible(visible)
        if visible == False and item == self._selected_item:
            visible_items = self.get_visible_items()
            if len(visible_items) == 0:
                self._selected_item = None
            else:
                self._selected_item = visible_items[0]
        # set selected if item is set to visible and none is selected
        elif self._selected_item is None:
            self._selected_item = item

    #override
    def get_bb(self):
        if not self.is_open():
            return self.dropdown_button_bb
        else:
            return get_group_bounding_box(self.get_visible_items())

    def get_visible_items(self):
        i:int = 0
        first_bb = self.dropdown_button_bb
        available_items:list[DropdownItem] = []
        for item in self._all_items:
            #TODO: check if window bounds are surpassed by any item's next_bb
            next_bb = BoundingBox(first_bb.x, first_bb.y + first_bb.height*i, first_bb.width, first_bb.height)
            if item.is_visible():
                item.set_bb(next_bb)
                available_items.append(item)
                i += 1
        return available_items
        
    def set_selected_item(self, ddi:DropdownItem):
        for item in self._all_items:
            if item == ddi:
                item.set_selected(True)
                self._selected_item = item
            else:
                item.set_selected(False)

    def get_selected_item(self) -> DropdownItem:
        return self._selected_item

    def get_current_value(self):
        if self.get_selected_item() is not None:
            return self.get_selected_item().get_value()
        else:
            return None
    
    def render(self, img: np.ndarray) -> np.ndarray:
        if self.is_open():
            for item in self.get_visible_items():
                item.render(img)
        else:
            #TODO
            pass
        return img

  