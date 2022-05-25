import unittest
import numpy as np

from app.dropdown import Dropdown
from exception import InvalidInputError, ArgumentError

TEST_STATE_SECTOR = np.array([0,0,0,0,0], dtype=int)
TEST_NAME = "default.test.dropdown"

class DropdownTest(unittest.TestCase):
  def test_empty_items(self):
    with self.assertRaises(ValueError) as context:
      Dropdown(TEST_STATE_SECTOR, TEST_NAME, [])

if __name__=="__main__":
  unittest.main()

def run():
  unittest.main()