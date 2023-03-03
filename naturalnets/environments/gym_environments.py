import gymnasium as gym
import numpy as np
from gymnasium.spaces.utils import flatdim

from naturalnets.environments.environment_utils import deprecate_environment
from naturalnets.environments.i_environment import IEnvironment


class GeneralGymEnvironment(IEnvironment):

    def __init__(self, env_seed: int, configuration: dict):
        deprecate_environment("GeneralGymEnv")
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
