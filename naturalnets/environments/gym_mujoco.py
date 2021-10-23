import numpy as np
import attr
import gym
from environments.i_environment import IEnvironment, registered_environment_classes


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class GymMujocoCfg:
    type: str
    name: str


class GymMujoco(IEnvironment):

    def __init__(self, env_seed: int, configuration: dict):

        self.config = GymMujocoCfg(**configuration)

        self.env = gym.make(self.config.name)

        self.env.seed(env_seed)

    def get_number_inputs(self):
        return self.env.observation_space.shape[0]

    def get_number_outputs(self):
        return self.env.action_space.shape[0]

    def reset(self):
        return self.env.reset()

    def step(self, action: np.ndarray):
        return self.env.step(action)

    def render(self):
        self.env.render()


# TODO: Do this registration via class decorator
registered_environment_classes['GymMujoco'] = GymMujoco
