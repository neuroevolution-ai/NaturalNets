import abc
import numpy as np

registered_environment_classes = {}


def get_environment_class(environment_class_name: str):
    if environment_class_name in registered_environment_classes:
        return registered_environment_classes[environment_class_name]
    else:
        raise RuntimeError("No valid environment")


class IEnvironment(abc.ABC):

    @abc.abstractmethod
    def get_number_inputs(self):
        pass

    @abc.abstractmethod
    def get_number_outputs(self):
        pass

    @abc.abstractmethod
    def reset(self, env_seed: int):
        pass

    @abc.abstractmethod
    def step(self, action: np.ndarray):
        pass
