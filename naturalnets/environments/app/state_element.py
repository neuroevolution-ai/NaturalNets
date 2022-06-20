import numpy as np

from typing import List
from naturalnets.environments.app.exception import ArgumentError
from naturalnets.environments.app.interfaces import Renderable

class StateElement(Renderable):
    def __init__(self, state_len:int):
        self._state:np.ndarray = np.zeros(state_len, dtype=int)
        self._children:list['StateElement'] = []

    def get_state(self) -> np.ndarray:
        return self._state

    def get_state_len(self) -> int:
        return len(self.get_state())
        
    def assign_state_sector(self, state_sector:np.ndarray):
        if not np.array_equal(np.zeros(len(state_sector)), state_sector):
            # throw error to emphasize that state_sector state would be overwritten
            # i.e. state cannot be set with this method
            raise ArgumentError("Given state sector is not empty.")
        
        current_state = np.copy(self.get_state())
        self._state = state_sector
        self._state[:] = current_state[:]

    def get_children(self) -> List['StateElement']:
      return self._children

    def add_child(self, child: 'StateElement'):
        self.get_children().append(child)
        
    def add_children(self, children:List['StateElement']):
        for child in children:
            self.add_child(child)