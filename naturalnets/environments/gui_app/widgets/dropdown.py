""" Module containing classes relevant for the dropdown-widget."""
from typing import Any, List, Optional, Tuple

import cv2
import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.gui_app.interfaces import Clickable
from naturalnets.environments.gui_app.page import Widget
from naturalnets.environments.gui_app.utils import get_group_bounding_box, put_text


class DropdownItem(Widget):
    """Widget representing a single dropdown-item.

       State description:
            state[0]: the selected-state of this dropdown-item.
    """
    STATE_LEN = 1

    def __init__(self, value, display_name: str):
        """
        The BoundingBox of this widget is set by the corresponding dropdown and
        is thus not passed to the constructor.

        Args:
            value (_type_): The value that this dropdown-item represents.
            display_name (str): The string representation that is shown when rendering
            this dropdown-item.
        """
        # BoundingBox is set by/depends on Dropdown
        super().__init__(self.STATE_LEN, BoundingBox(0, 0, 0, 0))
        # Like in CheckBox and other places use 0 as False, and 1 as True.
        # This ties in with the state vector, as it contains either zeros or ones.
        self._is_visible = 1
        self._value = value
        self.get_state()[0] = 0  # is-selected state
        self.display_name = display_name

    def get_value(self):
        return self._value

    def is_visible(self) -> int:
        return self._is_visible

    def set_visible(self, visible: int) -> None:
        """Sets the visible-status (denoting if this item shows up in the dropdown) of this
        dropdown-item.
        """
        self._is_visible = visible

    def handle_click(self, click_position: np.ndarray) -> None:
        """Currently unused method. May be used to perform on-click actions.
        """

    def set_selected(self, selected: int):
        self.get_state()[0] = selected

    def is_selected(self) -> int:
        return self.get_state()[0]

    def render(self, img: np.ndarray) -> np.ndarray:
        x, y, width, height = self.get_bb().get_as_tuple()
        start_point = (x, y)
        end_point = (x + width, y + height)
        color = Color.BLACK.value
        thickness = 2
        cv2.rectangle(img, start_point, end_point, color, thickness)

        text_padding = 3 * thickness
        bottom_left_corner = (x + text_padding, y + height - text_padding)
        if self.display_name is not None:
            put_text(img, self.display_name, bottom_left_corner, font_scale=0.4)
        else:
            put_text(img, self.get_value(), bottom_left_corner, font_scale=0.4)

        return img


class Dropdown(Widget):
    """Widget representing a dropdown. May hold multiple dropdown items, managing
    their selected-state.

       State description:
            state[0]: the opened-state of this dropdown.
    """
    STATE_LEN = 1

    def __init__(self, bounding_box: BoundingBox, items: List[DropdownItem]):
        """
        Args:
            bounding_box (BoundingBox): The BoundingBox of the dropdown (i.e. the dropdown-button).
            items (List[DropdownItem]): List containing dropdown-items, may be empty.
        """
        super().__init__(self.STATE_LEN, bounding_box)
        self._dropdown_button_bb = bounding_box
        self._all_items: List[DropdownItem] = items
        self.add_children(self._all_items)
        self._selected_item: DropdownItem = None

        self._update_item_bounding_boxes()

    def is_open(self) -> int:
        return self.get_state()[0]

    def open(self):
        """Opens the dropdown, if it contains at least one item.
        """
        if len(self.get_visible_items()) > 0:
            self.get_state()[0] = 1

    def close(self):
        self.get_state()[0] = 0

    def handle_click(self, click_position: np.ndarray) -> None:
        """Sets the selected dropdown-item, if any. Closes the
        dropdown if it was open.

        Args:
            click_position (np.ndarray): the position of the click.
        """
        if self.is_open():
            for item in self._update_item_bounding_boxes():
                if item.is_clicked_by(click_position):
                    self.set_selected_item(item)
            # any click action closes dropdown if it was open
            self.close()
        else:
            self.open()

    def calculate_distance_to_click(self, click_position: np.ndarray, current_minimal_distance: Optional[float],
                                    current_clickable: Optional[Clickable]) -> Tuple[float, Clickable]:
        if self.is_open():
            for item in self._update_item_bounding_boxes():
                current_minimal_distance, current_clickable = item.calculate_distance_to_click(
                    click_position, current_minimal_distance, current_clickable
                )
            return current_minimal_distance, current_clickable
        else:
            return super().calculate_distance_to_click(click_position, current_minimal_distance, current_clickable)

    def get_bb(self):
        if not self.is_open():
            return self._dropdown_button_bb

        return get_group_bounding_box(self._update_item_bounding_boxes())

    def _update_item_bounding_boxes(self) -> List[DropdownItem]:
        """Recalculates the bounding-boxes of the visible items in this Dropdown
        (bounding-boxes/positions of the items depend on which items are shown)

        Returns the visible items."""
        i: int = 0
        first_bb = self._dropdown_button_bb
        visible_items: List[DropdownItem] = []
        for item in self._all_items:
            if item.is_visible():
                # TODO: Depending on the position of the dropdown and the number of items,
                # the bounding box of the dropdown may surpass the window size of the app.
                # In the current state of the app no dropdown surpasses the window bounds.
                # If new dropdowns are added to the app or the dropdown class is used in
                # a different project, an automatic check should be implemented or all dropdowns
                # checked manually.
                next_bb = BoundingBox(first_bb.x, first_bb.y + first_bb.height * i,
                                    first_bb.width, first_bb.height)
                item.set_bb(next_bb)
                visible_items.append(item)
                i += 1
        return visible_items

    def get_visible_items(self) -> List[DropdownItem]:
        visible_items: List[DropdownItem] = []
        for item in self._all_items:
            if item.is_visible():
                visible_items.append(item)
        return visible_items

    def get_all_items(self):
        return self._all_items

    def set_selected_item(self, ddi: Optional[DropdownItem]):
        if self._selected_item is not None:
            self._selected_item.set_selected(0)

        if ddi is None:
            self._selected_item = None
            return

        ddi.set_selected(1)
        self._selected_item = ddi

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
                return

    def render(self, img: np.ndarray) -> np.ndarray:
        if self.is_open():
            for item in self._update_item_bounding_boxes():
                item.render(img)
        else:  # Render the selected item on the dropdown-button position if the dropdown is closed
            x, y, _, height = self.get_bb().get_as_tuple()
            text_padding = 6
            bottom_left_corner = (x + text_padding, y + height - text_padding)
            display_text = ""
            if self.get_current_value() is not None:
                display_text = self.get_selected_item().display_name
            put_text(img, display_text, bottom_left_corner, font_scale=0.4)

        return img
