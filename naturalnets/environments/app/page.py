import numpy as np

from abc import ABC, abstractmethod

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.state_manipulator import StateManipulator

class Page(StateManipulator):
    @abstractmethod
    @staticmethod
    def get_state_len(self):
        pass

    @abstractmethod
    @staticmethod
    def get_widget_dicts(self):
        pass

    @abstractmethod
    @staticmethod
    def get_accessor(self):
        pass

    def _init__(self, state_sector:np.ndarray, bounding_box:BoundingBox, widgets):
        super().__init__(state_sector)

    @abstractmethod
    def render(self, img:np.ndarray):
        pass
