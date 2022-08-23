import attr
import gym
import numpy as np

from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes
from naturalnets.tools.utils import rescale_values


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class GymMujocoCfg:
    type: str
    name: str


class GymMujoco(IEnvironment):

    def __init__(self, env_seed: int, configuration: dict):

        self.config = GymMujocoCfg(**configuration)

        self.env = gym.make(self.config.name)

        self.env.seed(env_seed)

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

    def reset(self):
        return self.env.reset()

    def step(self, action: np.ndarray):
        # We settled on the fact that every brain outputs values between [-1, 1]. If this particular Gym MuJoCo
        # environment has another value range, we need to transform the actions from the brain to that range
        if self.action_space_low != -1 or self.action_space_high != -1:
            rescale_values(action, previous_low=-1, previous_high=1, new_low=self.action_space_low,
                           new_high=self.action_space_high)

        return self.env.step(action)

    def render(self):
        self.env.render()


# TODO: Do this registration via class decorator
registered_environment_classes["GymMujoco"] = GymMujoco
