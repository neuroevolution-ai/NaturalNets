import abc
from typing import Optional, Dict, Type, Union

import numpy as np

registered_environment_classes = {}


def get_environment_class(environment_class_name: str) -> Union[Type["IEnvironment"], Type["IGUIEnvironment"]]:
    if environment_class_name in registered_environment_classes:
        return registered_environment_classes[environment_class_name]
    else:
        raise RuntimeError(f"'{environment_class_name}' is not a valid environment. Please choose one from the\n"
                           f"following list: {list(registered_environment_classes)!r}")


def register_environment_class(environment_class):
    registered_environment_classes[environment_class.__name__] = environment_class
    return environment_class


class IEnvironment(abc.ABC):

    @abc.abstractmethod
    def __init__(self, configuration: dict, **kwargs):
        pass

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

    @abc.abstractmethod
    def render(self, enhancer_info: Optional[Dict[str, np.ndarray]] = None):
        pass


class IGUIEnvironment(IEnvironment):
    @abc.abstractmethod
    def reset(self, env_seed: Optional[int]):
        pass

    @abc.abstractmethod
    def get_window_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_screen_size(self) -> int:
        pass

    @abc.abstractmethod
    def render_image(self) -> np.ndarray:
        pass

    @abc.abstractmethod
    def get_observation_dict(self) -> dict:
        pass
