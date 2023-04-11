import abc
from typing import List

import numpy as np

from naturalnets.environments.password_manager_app.utils import generate_reward_mapping_from_template


class RewardElement(abc.ABC):
    """
    Elements that give out reward for actions should inherit this class.

    Each element must define a reward_template which will be used to create a reward mapping automatically, once the
    constructor of this class is called. The reward_mapping is a dict, that allows to find the index of the specific
    reward in the reward array, a NumPy array. Use register_selected_reward to set the entry in the array to 1, to
    indicate the specific reward has been set.

    Example: If the class has a checkbox that shall give a reward twice, once if the checkbox was initially clicked,
    and once if the checkbox was initially deselected. Then reward_template should be {"my_checkbox": [False, True]},
    and the mapping will automatically set, that the class has a reward_count of 2, and the mapping sets False to
    index 0, and True to index 1. If the user clicks that checkbox, use register_selected_reward(["my_checkbox", True]),
    and reward_array will have a 1, in the second entry of the array.
    Note, that "my_checkbox" is a string that the user defines, and the call to register_selected_reward must also be
    done by the user at the correct location.
    """

    def __init__(self):
        self.reward_mapping, self.reward_count = None, None
        self.reward_array = None
        self.create_reward_mapping()

        self._reward_children: List["RewardElement"] = []

    @property
    @abc.abstractmethod
    def reward_template(self):
        pass

    def create_reward_mapping(self):
        self.reward_mapping, self.reward_count = generate_reward_mapping_from_template(self.reward_template, {}, 0)

    def get_reward_count(self):
        return self.reward_count

    def assign_reward_slice(self, reward_slice: np.ndarray):
        self.reward_array = reward_slice

    def register_selected_reward(self, reward_keys: List[str]):
        index = self.reward_mapping
        for key in reward_keys:
            index = index[key]
        self.reward_array[index] = 1

    def set_reward_children(self, children: List["RewardElement"]):
        self._reward_children = children

    def get_reward_children(self):
        return self._reward_children
