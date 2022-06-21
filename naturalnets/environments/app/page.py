import cv2
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.interfaces import Clickable, Renderable
from naturalnets.environments.app.utils import render_onto_bb
from naturalnets.environments.app.state_element import StateElement

class Widget(StateElement, Clickable):
    def __init__(self, state_len:int, bounding_box:BoundingBox):
        super().__init__(state_len)
        self._bounding_box = bounding_box

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box
        

class Page(StateElement, Clickable):
    def __init__(self, state_len:int, bounding_box:BoundingBox, img_path:str):
        super().__init__(state_len)
        self._bounding_box = bounding_box
        self._img_path = img_path
        self.widgets:list[Widget] = []
        pass

    def get_img_path(self):
        return self._img_path

    def get_bb(self) -> BoundingBox:
        return self._bounding_box

    def set_bb(self, bounding_box: BoundingBox) -> None:
        self._bounding_box = bounding_box
        
    def add_widget(self, widget:Widget):
        """Adds the widget to this Page. This will also add the widget to the
        pages' StateElement-children.
        """
        self.widgets.append(widget)
        self.add_child(widget)

    def get_widgets(self):
        return self.widgets
    
    def render(self, img:np.ndarray):
        to_render = cv2.imread(self._img_path)
        img = render_onto_bb(img, self.get_bb(), to_render)
        for widget in self.get_widgets():
            img = widget.render(img)
        return img