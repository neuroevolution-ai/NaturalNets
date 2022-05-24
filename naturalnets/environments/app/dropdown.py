import numpy as np

from typing import List, Dict
from widget import Widget
from exception import InvalidInputError, ArgumentError

class Dropdown(Widget):
  #TODO: settings might change the selected dropdown item (if the first item is selected
  # but then disabled in settings, the dropdown is set to the second item, etc.)

  #TODO: as constrains are used right now, they can be passed as a list
  #      (no need for self.constraints either)

  #TODO: refactor s.t. items are given as Dict[str,int] with initial values (from CALC_WIDGET_DICT)
  # state_h can then just be that dict and initial_values is made obsolete
  def __init__(self, state_sector:np.ndarray, name: str, items: List[str], constraints: Dict[str,str] = None, initial_state: np.ndarray = None):
    # TODO: maybe assert smth
    if len(items) < 1:
      raise ValueError("Attempting to build a dropdown with no items.")

    self._state_len:int = 1 + len(items) # all dropdown items + the dropdown button itself
    if len(state_sector) != self._state_len:
      raise ValueError("State section passed to dropdown is too small.")

    # populate is_constrained array (contains True if the state-value at that index is constrained)
    self.is_item_constrained_arr = []
    if constraints != None:
      self.is_item_constrained_arr:np.ndarray = np.array([True if item in constraints else False for item in items], dtype=bool)

    self._state = state_sector
    if initial_state != None:
      self.validate_initial_state(initial_state)
      #self._state:np.ndarray = initial_state.copy()
      self._state[:] = initial_state
    else:
      #self._state:np.ndarray = np.zeros(self._state_len, dtype=int)
      self._state[1] = 1 # first dropdown item is selected on automatic initialization
    
    self.validate_initial_state(self._state)

    self._element_name_to_index = {name: 0}
    for i in range(len(items)):
      self._element_name_to_index[items[i]] = i+1

    # human-readable state
    self.state_h:Dict[str, int] = self.build_state_h(name, items)

  def get_element_name_to_index(self) -> Dict[str,int]:
    return self._element_name_to_index

  def get_items(self):
    return self._state[1:]

  def select_first_available_item(self, constraint_state):
    assert self._state[0] == 0
    item_found = False
    for i in range(len(self.get_items())):
      state_index = i+1
      if item_found:
        self._state[state_index] = 0
        continue
      # item without constraints can always be selected
      if self.is_item_constrained_arr[i] == 0 or constraint_state[i] == 1:
        self._state[state_index] = 1
        item_found = True
        continue
      self._state[state_index] = 0
    if not item_found:
      raise ValueError("Attempting to select first item in dropdown, but no suitable item was found.")

  def build_state_h(self, name:str, items:List[str]):
    items_dict = {items[i]: self._state[i+1] for i in range(len(items))}

    state_h = {name: self._state[0], **items_dict}
    assert len(state_h) == self._state_len

    return state_h

  def get_state_h(self) -> Dict[str,int]:
    #TODO: test if state_h is automatically kept cince pointer at state
    #i = 0
    #for key in self.state_h:
    #  self.state_h[key] = self._state[i]
    #  i = i+1
    return self.state_h

  #def is_interactable(self) -> bool:
  #    return True

  #def get_human_readable_representation(self, index: int):
  #  return self.identifiers[index]

  #def get_human_readable_representation(self):
  #  return self.identifiers

  """
  def handle_input(self, input:np.ndarray, constraint_state:np.ndarray=None) -> np.ndarray:

    self.validate_input(input) # throws InvalidInputError
    #if not self.validate_input(input):
    #  raise InvalidInputError("Invalid input passed.")

    #if np.all(np.equal(input, self.state)):
    #  return self.state

    if not self.validate_constraints(input, constraint_state):
      raise InvalidInputError("Constraint check failed.")

    case = np.sum(input)
    # case == 1 is invalid
    if case == 2: # dropdown opened
      assert input[0] == 1
      if self.state[0] == 1:
        self.state[0] = 0
      else:
        self.state[0] = 1
    if case == 3: # value changed
      assert self.state[0] == 1 and input[0] == 1
      self.state[0] = 0 # close dropdown
      for i in range(1, len(self.state)):
        if self.state[i] == input[i]:
          self.state[i] = 0
        else:
          self.state[i] = input[i]

    self.validate_initial_state(self.state) # TODO: should not be necessary here, state should be kept consistent throughout all methods
    return self.state
  """

  #TODO: example for valid input
  # self.state:            [1, 1, 0, 0, 0, 0]
  # input:                 [1, 1, 0, 0, 1, 0]
  """
  Input vector of form: [is_dropdown_open, *items]
  """
  def _validate_input(self, input:np.ndarray) -> None:
    if (input is None or len(input) != self._state_len):
      raise InvalidInputError("Input == None or input length does not match state length.")

    sum_selected_items:int = np.sum(input[1:])
    #TODO: maybe check if dropdown was closed (is closing the  dropdown without choosing an item an option?)
    # At least one value has to be selected in any dropdown.
    if (sum_selected_items < 1):
      raise InvalidInputError("Input contains no selected items.")

    # max. two items can be selected in input vector (one is always selected)
    if (sum_selected_items > 2):
      raise InvalidInputError("Input contains more than two selected items.")

    # check if dropdown is open
    if (sum_selected_items == 2 and not self.is_dropdown_open()):
      raise InvalidInputError("Input contains two selected items, but the dropdown is not open.")

  """
  input: numpy array of length n
  constraint_state: numpy array of length n-1
  """
  #TODO: probably a responsibility of app
  def _validate_constraints(self, input:np.ndarray, constraint_state:np.ndarray) -> None:
    if len(self.is_item_constrained_arr) == 0:
      return True
    elif constraint_state == None:
      raise ArgumentError("Constraints need to be passed to step for Elements that have constraints.")

    if (len(constraint_state) != len(self.get_items())):
      raise ArgumentError("Passed constraint length does not match element contraint length.")

    for i in range(len(self.get_items())):
      if (input[i+1] and not self._state[i+1] and # input item is newly selected item
          self.is_item_constrained_arr[i] and not constraint_state[i]):
        raise InvalidInputError("Constrains check failed for given input.")


  def _mutate_state(self, input:np.ndarray) -> np.ndarray:
    case = np.sum(input)
    # case == 1 is invalid
    if case == 2: # dropdown opened
      assert input[0] == 1
      if self._state[0] == 1:
        self._state[0] = 0
      else:
        self._state[0] = 1
    if case == 3: # value changed
      assert self._state[0] == 1 and input[0] == 1
      self._state[0] = 0 # close dropdown
      for i in range(1, len(self._state)):
        if self._state[i] == input[i]:
          self._state[i] = 0
        else:
          self._state[i] = input[i]

    self.validate_initial_state(self._state) # TODO: should not be necessary here, state should be kept consistent throughout all methods
    print("dropdown mutated state: ", self._state)


  def get_state(self) -> np.ndarray:
    return self._state

  def is_dropdown_open(self) -> bool:
    return self._state[0] == 1

  def validate_initial_state(self, state:np.ndarray, constraint_state:np.ndarray=None) -> None:
    if len(state) != self._state_len:
      raise ValueError("State vector size and given vector size do not match.")

    sum_selected_items = np.sum(state[1:])
    if sum_selected_items != 1:
      raise ValueError("Exactly one item has to be selected in any valid dropdown state")
    
    if constraint_state != None:
      self.check_contraints(state, constraint_state)

      


  # handels closing itself, since all 'next' actions when open must be
  # on the dropdown
  def exec_on_next_step(self) -> None:
    pass
    #if self._state[0] == 1:
    #  self._state[0] = 0




