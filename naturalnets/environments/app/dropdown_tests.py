import unittest
import numpy as np

from dropdown import Dropdown
#from naturalnets.environments.app.exception import InvalidInputError
from exception import InvalidInputError, ArgumentError

TEST_STATE_SECTOR = np.array([0,0,0,0,0], dtype=int)
TEST_ITEMS = ["item.1", "item.2", "item.3", "item.4"]
TEST_STATE = np.array([0, 1, 0, 0, 0])
TEST_ITEMS_EMPTY = []

INVALID_INPUTS = [[0,0,0,0,0], [1,0,0,0,0], [0,1,0,1,0], 
                  [1,1,1,1,0], [1,1,1,1,1], None, [], [0,1,0,1,0,1], [0,0]]

CONSTRAINTS = {"item.1": "", "item.2": "", "item.4": ""}

class TestDropdown(unittest.TestCase):
  def test_empty_items(self):
    with self.assertRaises(ValueError) as context:
      Dropdown("empty", TEST_ITEMS_EMPTY)
  
  def test_successful_instantiation(self):
    dd = Dropdown("success", TEST_ITEMS)
    np.testing.assert_array_equal(dd.get_state(), TEST_STATE)

  def test_value_change(self):
    dd = Dropdown("name", TEST_ITEMS)
    # input and state are equal
    valid_input = [0,1,0,0,0]
    np.testing.assert_array_equal(dd.get_state(), valid_input)
    state = dd.step(valid_input)
    np.testing.assert_array_equal(state, valid_input)

    # input opens dropdown
    valid_input = [1,1,0,0,0]
    state = dd.step(valid_input)
    np.testing.assert_array_equal(state, valid_input)

    # value changed to second value
    valid_input = [1,1,1,0,0]
    expected_state = [0,0,1,0,0]
    state = dd.step(valid_input)
    np.testing.assert_array_equal(state, expected_state)

  def test_invalid_inputs(self):
    dd = Dropdown("name", TEST_ITEMS)
    for invalid_input in INVALID_INPUTS:
      with self.assertRaises(InvalidInputError) as context:
        dd.step(invalid_input)

  def test_initial_state(self):
    dropdown_open = [1,1,0,0,0]
    dd = Dropdown("name", TEST_ITEMS, initial_state=dropdown_open)
    np.testing.assert_array_equal(dd.get_state(), dropdown_open)

    # dropdown initialized on other value (default is first)
    dd = Dropdown("name", TEST_ITEMS, initial_state=[0,0,0,1,0])
    np.testing.assert_array_equal(dd.get_state(), [0,0,0,1,0])

    # two items selected initially
    with self.assertRaises(ValueError) as context:
      dd = Dropdown("name", TEST_ITEMS, initial_state=[1,0,1,1,0])

    # no items selected initially
    with self.assertRaises(ValueError) as context:
      dd = Dropdown("name", TEST_ITEMS, initial_state=[0,0,0,0,0])

        
  def test_constraints(self):
    # TODO: dropdown open in initial state? should probably not be possibru
    init_state = [1,1,0,0,0]
    dd = Dropdown("name", TEST_ITEMS, constraints=CONSTRAINTS, initial_state=init_state)
    with self.assertRaises(ArgumentError) as context:
      input = [1,1,1,0,0]
      state = dd.step(input)

    #test InvalidInputError
    invalid_constraints = [[0,0,0,1], [0,0,1,0], [1,0,0,0]]
    for invalid_constraint in invalid_constraints:
      with self.assertRaises(InvalidInputError) as context:
        dd.step([1,1,1,0,0], invalid_constraint)

    #test ArgumentError
    invalid_constraints = [None, [0,1], [0,1,0,0,0]]
    for invalid_constraint in invalid_constraints:
      with self.assertRaises(ArgumentError) as context:
        dd.step([1,1,1,0,0], invalid_constraint)

    # input == state, constraints should not matter
    # TODO: really? probably dropdown should close (since apperantly the already selected item
    # item was selected) -> state afterwards: [0,1,0,0,0], constraints should be checked
    dd.step([1,1,0,0,0], [0,0,0,0])

    # select first item
    dd.select_first_available_item([1,0,0,0])
    np.testing.assert_array_equal(dd.get_state(), [0,1,0,0,0])
    # open dropdown
    dd.step([1,1,0,0,0], [0,1,0,0])
    np.testing.assert_array_equal(dd.get_state(), [1,1,0,0,0])
    # select second item
    dd.step([1,1,1,0,0], [0,1,0,0])
    np.testing.assert_array_equal(dd.get_state(), [0,0,1,0,0])

    # select first item
    dd.select_first_available_item([1,0,0,0])
    np.testing.assert_array_equal(dd.get_state(), [0,1,0,0,0])
    # open dropdown
    dd.step([1,1,0,0,0], [0,1,0,0])
    np.testing.assert_array_equal(dd.get_state(), [1,1,0,0,0])

    # select last item 
    dd.step([1,1,0,0,1], [0,0,0,1])
    np.testing.assert_array_equal(dd.get_state(), [0,0,0,0,1])

  #TODO: test constraints

if __name__=="__main__":
  unittest.main()


