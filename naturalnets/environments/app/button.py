import numpy as np
from exception import ArgumentError, InvalidInputError

from widget import Widget_old
from typing import Dict, Callable

# TODO: probably not needed, since buttons do not change state, thus not beeing of relevance
#       for the output state to the neural net

class Button(Widget_old):
    """Widget representing a Button. It's own state is always [0].
    It modifies app state through the on_click method passed on instantiation.
    """

    def __init__(self, name:str, state_sector:np.ndarray, on_click:Callable):
        super().__init__(state_sector, name)
        if len(state_sector) != 1:
            raise ArgumentError("State sector for Button needs to have length of 1.")

        self._on_click = on_click

    def _validate_state(self, state:np.ndarray) -> bool:
        return len(state) == 1 and state[0] == 0

    def get_element_name_to_index(self) -> Dict[str,int]:
        return {self.get_name(): 0}

    def _validate_input(self, input:np.ndarray) -> None:
        if len(input) != 1:
            raise InvalidInputError("Button input length needs to be 1.")
        if input[0] != 1:
            raise InvalidInputError("Button input[0] needs to be 1")

    def _mutate_state(self, input:np.ndarray) -> None:
        """ 
        Mutates app state by calling the on_click function defined on instantiation.
        The buttons own state is always [0]!

            Parameters:
                input (np.ndarray): input validated by _validate_input(input).
        """

        if input is None:
            self._on_click()
        else:
            self._on_click(*input)

    # Buttons' state never changes -> not needed
    def exec_on_invalid_action(self) -> None:
        pass