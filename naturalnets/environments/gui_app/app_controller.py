from copy import copy

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.main_window import MainWindow
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.settings_window import SettingsWindow
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.widgets.button import Button


class AppController:
    """Controller-class that builds all components of the app, initializes the app state-vector
    and delegates clicks to the app components (acts as the click- and render-root of the app).
    """
    SETTINGS_BUTTON_BB = BoundingBox(8, 0, 49, 18)

    def __init__(self):
        self.main_window = MainWindow()
        self.settings_window = SettingsWindow(self.main_window)

        self.settings_button = Button(self.SETTINGS_BUTTON_BB, self.settings_window.open)

        self._total_state_len = 0
        self._total_state_len += self.get_element_state_len(self.main_window)
        self._total_state_len += self.get_element_state_len(self.settings_window)

        self._state = np.zeros(self._total_state_len, dtype=np.int8)
        self._last_allocated_state_index = 0

        states_info = []
        self.assign_state(self.main_window, 0, states_info)
        self.assign_state(self.settings_window, 0, states_info)
        self._states_info = states_info

        self.reward_array = None
        self.reset_reward_array()

    def calculate_reward_count(self, reward_count, reward_element: RewardElement):
        reward_count += reward_element.get_reward_count()

        for child in reward_element.get_reward_children():
            reward_count = self.calculate_reward_count(reward_count, child)

        return reward_count

    def reset_reward_array(self):
        reward_count = self.calculate_reward_count(0, self.main_window)
        reward_count = self.calculate_reward_count(reward_count, self.settings_window)

        self.reward_array = np.zeros(reward_count, dtype=np.uint8)

        last_reward_index = self.assign_reward(0, self.main_window)
        last_reward_index = self.assign_reward(last_reward_index, self.settings_window)
        assert last_reward_index == reward_count

    def assign_reward(self, current_index, reward_element: RewardElement):
        reward_count = reward_element.get_reward_count()
        reward_element.assign_reward_slice(self.reward_array[current_index:current_index + reward_count])
        current_index += reward_count

        for reward_child in reward_element.get_reward_children():
            current_index = self.assign_reward(current_index, reward_child)

        return current_index

    def reset(self):
        self.main_window.reset()

        self.settings_window.close()
        self.settings_window.reset()

        self.reset_reward_array()

        self._state = np.zeros(self._total_state_len, dtype=np.int8)
        self._last_allocated_state_index = 0

        self.assign_state(self.main_window, 0, [])
        self.assign_state(self.settings_window, 0, [])

    def get_element_state_len(self, state_element: StateElement) -> int:
        """Collects the total state length of the given StateElement and all its children.

        Args:
            state_element (StateElement): the state element.

        Returns:
            int: the total state length of the given StateElement and all of its children.
        """
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
                "class_name": str(type(state_element)).split('.')[-1][:-2],
                "recursion_depth": str(recursion_depth)
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
        """Returns the app's total state.
        """
        return self._state

    def get_states_info(self) -> list:
        """Returns the app's info for the state vector as a list containing all states.
        """
        return self._states_info

    def get_total_state_len(self) -> int:
        """Returns the app's total state length.
        """
        return self._total_state_len

    def get_total_reward_len(self) -> int:
        """Returns the amount of reward, that is achievable."""
        return len(self.reward_array)

    def handle_click(self, click_position: np.ndarray):
        """Delegates click-handling to the clicked component.
        """
        previous_reward_array = copy(self.reward_array)

        if self.settings_window.is_open():
            self.settings_window.handle_click(click_position)
        elif (not self.main_window.current_page_blocks_click()
              and self.settings_button.is_clicked_by(click_position)):
            self.settings_window.open()
        else:
            self.main_window.handle_click(click_position)

        reward = np.count_nonzero(previous_reward_array != self.reward_array)

        return reward

    def render(self, img: np.ndarray) -> np.ndarray:
        """Calls the main window rendering method and the settings window rendering method,
        if the settings window is open.

        Args:
            img (np.ndarray): The cv2 image to render onto.
        """
        img = self.main_window.render(img)
        if self.settings_window.is_open():
            img = self.settings_window.render(img)
        return img

    def get_clickable_elements(self):
        # TODO remove this once finished
        return []

        if self.settings_window.is_open():
            return self.settings_window.get_clickable_elements()

        currently_visible_widgets = [self.settings_button]

        return self.main_window.get_widget_state(currently_visible_widgets)
