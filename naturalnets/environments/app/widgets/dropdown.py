""" Module containing classes relevant for the dropdown-widget.
"""
from typing import Any, List

import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.enums import Color
from naturalnets.environments.app.page import Widget
from naturalnets.environments.app.utils import get_group_bounding_box, put_text

class DropdownItem(Widget):
    """Widget representing a single dropdown-item.

       State description:
            state[0]: the selected-state of this dropdown-item.
    """
    STATE_LEN = 1

    def __init__(self, value, display_name:str):
        """
        The BoundingBox of this widget is set by the corresponding dropdown and
        is thus not passed to the constructor.

        Args:
            value (_type_): The value that this dropdown-item represents.
            display_name (str): The string representation that is shown when rendering
            this dropdown-item.
        """
        # BoundingBox is set by/depends on Dropdown
        super().__init__(self.STATE_LEN, BoundingBox(0,0,0,0))
        self._is_visible = True
        self._value = value
        self.get_state()[0] = 0 # is-selected state
        self.display_name = display_name

    def get_value(self):
        return self._value

    def is_visible(self) -> bool:
        return self._is_visible

    def set_visible(self, active:bool) -> None:
        """Sets the visible-status (denoting if this item shows up in the dropdown) of this 
        dropdown-item. Should only be accessed by the Dropdown-Class.
        """
        self._is_visible = active

    def handle_click(self, click_position: np.ndarray) -> None:
        """Currently unused method. May be used to perform on-click actions.
        """

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

        text_padding = 3*thickness
        bottom_left_corner = (x + text_padding, y + height - text_padding)
        if self.display_name is not None:
            put_text(img, self.display_name, bottom_left_corner, 0.4)
        else:
            put_text(img, self.get_value(), bottom_left_corner, 0.4)


        return img

class Dropdown(Widget):
    """Widget representing a dropdown. May hold multiple dropdown items, managing
    their selected-state.

       State description:
            state[0]: the opened-state of this dropdown.
    """
    STATE_LEN = 1

    def __init__(self, bounding_box:BoundingBox, items:List[DropdownItem]):
        """
        Args:
            bounding_box (BoundingBox): The BoundingBox of the dropdown (i.e. the dropdown-button).
            items (List[DropdownItem]): List containing dropdown-items, may be empty.
        """
        super().__init__(self.STATE_LEN, bounding_box)
        self._dropdown_button_bb = bounding_box
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

    def handle_click(self, click_position: np.ndarray) -> None:
        """Sets the selected drodpown-item, if any. Closes the 
        dropdown if it was open.

        Args:
            click_position (np.ndarray): the position of the click.
        """
        if self.is_open():
            for item in self.get_visible_items():
                if item.is_clicked_by(click_position):
                    self.set_selected_item(item)
            # any click action closes dropdown if it was open
            self.close()
        else:
            self.open()

    def set_visible(self, ddi:DropdownItem, visible:bool):
        index = self._all_items.index(ddi)
        item = self._all_items[index]
        item.set_visible(visible)

    #override
    def get_bb(self):
        if not self.is_open():
            return self._dropdown_button_bb

        return get_group_bounding_box(self.get_visible_items())

    def get_visible_items(self):
        i:int = 0
        first_bb = self._dropdown_button_bb
        available_items:list[DropdownItem] = []
        for item in self._all_items:
            #TODO: check if window bounds are surpassed by any item's next_bb 
            # (not necessary for this app)
            next_bb = BoundingBox(first_bb.x, first_bb.y + first_bb.height*i,
                                  first_bb.width, first_bb.height)
            if item.is_visible():
                item.set_bb(next_bb)
                available_items.append(item)
                i += 1
        return available_items

    def get_all_items(self):
        return self._all_items

    def set_selected_item(self, ddi:DropdownItem):
        if ddi is None:
            self._selected_item = None

        for item in self._all_items:
            if item == ddi:
                item.set_selected(True)
                self._selected_item = item
            else:
                item.set_selected(False)

    def get_selected_item(self) -> DropdownItem:
        return self._selected_item

    def get_current_value(self) -> Any:
        if self.get_selected_item() is not None:
            return self.get_selected_item().get_value()
        else:
            return None

    def set_selected_value(self, value) -> None:
        for item in self.get_visible_items():
            if item.get_value() == value:
                self.set_selected_item(item)

    def render(self, img: np.ndarray) -> np.ndarray:
        if self.is_open():
            for item in self.get_visible_items():
                item.render(img)
        else: # render selected item on dropdown-button position if dropdown is closed
            x, y, _, height = self.get_bb().get_as_tuple()
            text_padding = 6
            bottom_left_corner = (x + text_padding, y + height - text_padding)
            display_text = ""
            if self.get_current_value() is not None:
                display_text = self.get_selected_item().display_name
            put_text(img, display_text, bottom_left_corner, 0.4)

        return img
