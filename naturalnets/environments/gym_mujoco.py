from typing import Optional, Dict

import gym
import numpy as np
from attrs import define, field, validators

from naturalnets.environments.i_environment import IEnvironment, register_environment_class
from naturalnets.tools.utils import rescale_values


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class GymMujocoCfg:
    type: str = field(validator=validators.instance_of(str))
    name: str = field(validator=validators.instance_of(str))


@register_environment_class
class GymMujoco(IEnvironment):

    def __init__(self, configuration: dict):

        self.config = GymMujocoCfg(**configuration)

        # The new step API returns two booleans, terminated and truncated, to indicate if an environment is either
        # done (terminated) or met a truncation condition (truncated), e.g. a time limit
        self.env = gym.make(self.config.name)

        assert isinstance(self.env.action_space, gym.spaces.Box), ("Only environments with a Box action space "
                                                                   "(continuous values) are supported.")

        try:
            self.action_space_low = int(float(self.env.action_space.low_repr))
            self.action_space_high = int(float(self.env.action_space.high_repr))
        except ValueError:
            raise RuntimeError(f"Environment {self.config.name} provides an action space that has varying bounds "
                               f"(different high and low values per action space dimension), but "
                               f"only action spaces that have matching bounds in each dimension are allowed. "
                               f"Current environment bounds:\n"
                               f"Low: {self.env.action_space.low}\n"
                               f"High: {self.env.action_space.high}\n")

    def get_number_inputs(self):
        return self.env.observation_space.shape[0]

    def get_number_outputs(self):
        return self.env.action_space.shape[0]

    def reset(self, env_seed: int):
        return self.env.reset(seed=env_seed)[0]

    def step(self, action: np.ndarray):
        # We settled on the fact that every brain outputs values between [-1, 1]. If this particular Gym MuJoCo
        # environment has another value range, we need to transform the actions from the brain to that range
        if self.action_space_low != -1 or self.action_space_high != -1:
            rescale_values(action, previous_low=-1, previous_high=1, new_low=self.action_space_low,
                           new_high=self.action_space_high)

        ob, rew, terminated, truncated, info = self.env.step(action)

        # "Calculate" done to be True of either the environment ist terminated or truncated
        return ob, rew, terminated or truncated, info

    def render(self, enhancer_info: Optional[Dict[str, np.ndarray]] = None):
        self.env.render()
