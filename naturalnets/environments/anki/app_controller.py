from copy import copy

import numpy as np
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.anki.pages.main_page import MainPage
class AppController:
    
    def __init__(self):
        self.main_page = MainPage()
        self._total_state_len = self.get_element_state_len(self.main_page)
        
        states_info = []
        self.assign_state(self.main_page, 0, states_info)
        self._states_info = states_info
        
        self._state = np.zeros(self._total_state_len, dtype=np.int8)
        self._last_allocated_state_index = 0

        self.reward_array = None
        self.reset_reward_array()
    
    def calculate_reward_count(self, reward_count, reward_element: RewardElement):
        reward_count += reward_element.get_reward_count()

        for child in reward_element.get_reward_children():
            reward_count = self.calculate_reward_count(reward_count, child)

        return reward_count

    def reset_reward_array(self):
        reward_count = self.calculate_reward_count(0, self.main_page)
        self.reward_array = np.zeros(reward_count, dtype=np.uint8)
        last_reward_index = self.assign_reward(0, self.main_page)
        assert last_reward_index == reward_count

    def assign_reward(self, current_index, reward_element: RewardElement):
        reward_count = reward_element.get_reward_count()
        reward_element.assign_reward_slice(self.reward_array[current_index:current_index + reward_count])
        current_index += reward_count

        for reward_child in reward_element.get_reward_children():
            current_index = self.assign_reward(current_index, reward_child)

        return current_index

    def reset(self):
        self.reset_reward_array()

        self._state = np.zeros(self._total_state_len, dtype=np.int8)
        self._last_allocated_state_index = 0

        self.assign_state(self.main_page, 0, [])

    def get_element_state_len(self, state_element: StateElement) -> int:
        accumulated_len = 0
        for child in state_element.get_children():
            accumulated_len += self.get_element_state_len(child)
        accumulated_len += state_element.get_state_len()
        return accumulated_len
    
    def assign_state(self, state_element: StateElement, recursion_depth: int, states_info: list) -> None:
        """Assigns (part of) the app state-vector to the given StateElement and all of its children.

        Args:
            state_element (StateElement): the StateElement.
        """
        state_len = state_element.get_state_len()
        state_sector = self.get_next_state_sector(state_len)
        state_element.assign_state_sector(state_sector)

        for _ in range(state_len):
            states_info.append({
                'class_name': str(type(state_element)).split('.')[-1][:-2],
                'recursion_depth': str(recursion_depth)
            })

        for child in state_element.get_children():
            self.assign_state(child, recursion_depth+1, states_info)

    def get_next_state_sector(self, state_len):
        """Returns the next state sector (i.e. the next non-assigned part of the total
        app state-vector) given a state length.

        Args:
            state_len (_type_): the length of the desired state sector.
        """

        sector_end = self._last_allocated_state_index + state_len
        sector = self._state[self._last_allocated_state_index:sector_end]
        self._last_allocated_state_index = sector_end
        return sector

    def get_total_state(self) -> np.ndarray:
        return self._state

    def get_states_info(self) -> list:
        return self._states_info

    def get_total_reward_len(self) -> int:
        return len(self.reward_array)
    
    def get_total_state_len(self) -> int:
        return self._total_state_len
    
    def handle_click(self, click_position: np.ndarray):
        previous_reward_array = copy(self.reward_array)
        self.main_page.handle_click(click_position)
        reward = np.count_nonzero(previous_reward_array != self.reward_array)
        return reward
    
    def get_total_state(self) -> np.ndarray:
        return self._state

    def render(self,img: np.ndarray):
        img = self.main_page.render(img)
        return img