import numpy as np

from naturalnets.brains import IBrain
from naturalnets.brains.i_brain import register_brain_class


@register_brain_class
class RandomBrain(IBrain):
    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: dict,
                 brain_state: dict):
        self.output_size = output_size
        self.rng = np.random.default_rng()

    def step(self, u):
        return self.rng.uniform(low=-1.0, high=1.0, size=self.output_size)

    def reset(self):
        self.rng = np.random.default_rng()

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):
        return {}

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: dict):
        pass

    @classmethod
    def save_brain_state(cls, path, brain_state):
        pass
