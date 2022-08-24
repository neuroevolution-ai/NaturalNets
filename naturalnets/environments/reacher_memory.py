import attr
import gym
import numpy as np

from naturalnets.environments.environment_utils import deprecate_environment
from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class ReacherMemoryCfg:
    type: str
    frames_observation_phase: int
    frames_memory_phase: int
    frames_action_phase: int


class ReacherMemory(IEnvironment):

    def __init__(self, env_seed: int, configuration: dict):

        deprecate_environment("ReacherMemory")

        self.config = ReacherMemoryCfg(**configuration)

        self.env = gym.make("Reacher-v2")

        self.env.seed(env_seed)

        self.env._max_episode_steps = self.config.frames_observation_phase + self.config.frames_memory_phase + \
                                      self.config.frames_action_phase

        self.t = 0

    def get_number_inputs(self):
        return self.env.observation_space.shape[0]

    def get_number_outputs(self):
        return self.env.action_space.shape[0]

    def reset(self):
        return self.env.reset()

    def step(self, action: np.ndarray):

        if self.t <= self.config.frames_observation_phase + self.config.frames_memory_phase:
            action = np.zeros(self.get_number_outputs())

        ob, rew, done, info = self.env.step(action)

        if self.t >= self.config.frames_observation_phase:
            indices = [4, 5, 8, 9, 10]
            for index in indices:
                ob[index] = 0.0

        if self.t < self.config.frames_observation_phase + self.config.frames_memory_phase:
            rew = 0.0

        self.t += 1

        return ob, rew, done, info

    def render(self):
        self.env.render()


# TODO: Do this registration via class decorator
registered_environment_classes["ReacherMemory"] = ReacherMemory
