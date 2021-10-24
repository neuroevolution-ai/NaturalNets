import numpy as np
import gym
from gym.spaces.utils import flatdim

from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes


class GeneralGymEnvironment(IEnvironment):

    def __init__(self, env_seed: int, configuration: dict):
        self.configuration = configuration
        self.env = gym.make(configuration["env_id"])
        self.env.seed(env_seed)

    def get_number_inputs(self):
        return flatdim(self.env.observation_space)

    def get_number_outputs(self):
        return flatdim(self.env.action_space)

    def reset(self):
        return self.env.reset()

    def step(self, action: np.ndarray):
        return self.env.step(action)

    def render(self):
        self.env.render()


# TODO: Do this registration via class decorator
registered_environment_classes["GeneralGymEnv"] = GeneralGymEnvironment
