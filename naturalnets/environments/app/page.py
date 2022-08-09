from typing import List
import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.interfaces import Clickable, HasPopups
from naturalnets.environments.app.utils import render_onto_bb
from naturalnets.environments.app.state_element import StateElement

class Widget(StateElement, Clickable):
    """Represents a widget of the app, i.e. a clickable state-element.
    """
    def __init__(self, state_len:int, bounding_box:BoundingBox):
        super().__init__(state_len)
        self._bounding_box = bounding_box

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

class Page(StateElement, Clickable, HasPopups):
    """Represents a Page of the app (used in main-window and settings-window). A page
    may contain widgets and popups (in addition to non-widget state-elements). Popups block
    clicks to all other elements of the app. A page has it's own image that may be rendered
    onto the base app image."""

    def __init__(self, state_len:int, bounding_box:BoundingBox, img_path:str):
        super().__init__(state_len)
        self._bounding_box = bounding_box
        self._img_path = img_path
        self.widgets: List[Widget] = []

    def get_img_path(self) -> str:
        """Returns the path to this pages image file.

        Returns:
            str: the path to the pages' image file.
        """
        return self._img_path

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box

    def add_widget(self, widget:Widget):
        """Adds the given widget to this Page. This will also add the widget to the
        pages' StateElement-children."""
        self.widgets.append(widget)
        self.add_child(widget)

    def add_widgets(self, widgets:List[Widget]):
        """Adds the given widget-list to this Page. This will also add the widgets to the
        pages' StateElement-children."""
        for widget in widgets:
            self.add_widget(widget)

    def get_widgets(self) -> List[Widget]:
        """Returns all widgets of this page. Might differ from the pages' state-element children!"""
        return self.widgets

    def render(self, img:np.ndarray):
        """Renders this page as well as all of its widgets to the given image."""
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        for widget in self.get_widgets():
            img = widget.render(img)
        return img

    def is_popup_open(self) -> int:
        return 0

    def is_dropdown_open(self) -> bool:
        return False
