import numpy as np

from naturalnets.environments.password_manager_app.main_window import (
    MainWindow,
)
from naturalnets.environments.app_components.state_element import (
    StateElement,
)
from coverage import Coverage


class AppController:
    """Controller-class that builds all components of the app, initializes the
    app state-vector and delegates clicks to the app components (acts as the
    click- and render-root of the app).
    """

    main_window = MainWindow()

    def __init__(self, coverage_measurer: Coverage):
        self._total_state_len = 0
        self._total_state_len += self.get_element_state_len(AppController.main_window)

        self._state = np.zeros(self._total_state_len, dtype=np.int8)
        self._last_allocated_state_index = 0

        states_info = []
        self.assign_state(AppController.main_window, 0, states_info)
        self._states_info = states_info

        self.coverage_measurer = coverage_measurer

    def reset(self):
        AppController.main_window.reset()

        self._state = np.zeros(self._total_state_len, dtype=np.int8)
        self._last_allocated_state_index = 0

        self.assign_state(AppController.main_window, 0, [])

    def get_element_state_len(self, state_element: StateElement) -> int:
        """Collects the total state length of the given StateElement and
        all its children.

        Args:
            state_element (StateElement): the state element.

        Returns:
            int: the total state length of the given StateElement and
            all of its children.
        """
        accumulated_len = 0
        for child in state_element.get_children():
            accumulated_len += self.get_element_state_len(child)
        accumulated_len += state_element.get_state_len()
        return accumulated_len

    def assign_state(
        self,
        state_element: StateElement,
        recursion_depth: int,
        states_info: list,
    ) -> None:
        """Assigns (part of) the app state-vector to the given StateElement
        and all of its children.

        Args:
            state_element (StateElement): the StateElement.
        """
        state_len = state_element.get_state_len()
        state_sector = self.get_next_state_sector(state_len)
        state_element.assign_state_sector(state_sector)

        for _ in range(state_len):
            states_info.append(
                {
                    "class_name": str(type(state_element)).split(".")[-1][:-2],
                    "recursion_depth": str(recursion_depth),
                }
            )

        for child in state_element.get_children():
            self.assign_state(child, recursion_depth + 1, states_info)

    def get_next_state_sector(self, state_len):
        """Returns the next state sector (i.e. the next non-assigned part of
        the total app state-vector) given a state length.

        Args:
            state_len (_type_): the length of the desired state sector.
        """

        sector_end = self._last_allocated_state_index + state_len
        sector = self._state[self._last_allocated_state_index : sector_end]
        self._last_allocated_state_index = sector_end
        return sector

    def get_total_state(self) -> np.ndarray:
        """Returns the app's total state."""
        return self._state

    def get_states_info(self) -> list:
        """Returns the app's info for the state vector as a list
        containing all states."""
        return self._states_info

    def get_total_state_len(self) -> int:
        """Returns the app's total state length."""
        return self._total_state_len

    def handle_click(self, click_position: np.ndarray):
        """Delegates click-handling to the clicked component."""

        self.coverage_measurer.start()
        AppController.main_window.handle_click(click_position)
        self.coverage_measurer.stop()

        coverage_data = self.coverage_measurer.get_data()
        measured_files = coverage_data.measured_files()

        measured_lines = 0

        for measured_file in measured_files:
            measured_lines += len(coverage_data.lines(measured_file))

        return measured_lines

    def render(self, img: np.ndarray) -> np.ndarray:
        """Calls the main window rendering method.

        Args:
            img (np.ndarray): The cv2 image to render onto.
        """
        img = AppController.main_window.render(img)
        return img
