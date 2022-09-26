from abc import ABC, abstractmethod
from typing import Tuple, Dict, Optional

import attr
import numpy as np

registered_enhancers = {}


def get_enhancer_class(enhancer_class_name: str):
    if enhancer_class_name in registered_enhancers:
        return registered_enhancers[enhancer_class_name]
    else:
        raise RuntimeError(f"'{enhancer_class_name}' is not a valid enhancer. Please choose one from the following "
                           f"list: {list(registered_enhancers)!r}")


def register_enhancer_class(enhancer_class):
    registered_enhancers[enhancer_class.__name__] = enhancer_class
    return enhancer_class


@attr.s(slots=True, auto_attribs=True, frozen=True)
class IEnhancerCfg(ABC, dict):
    type: str


class IEnhancer(ABC):

    def __init__(self, env_output_size: int):
        self.env_output_size = env_output_size

    @abstractmethod
    def get_number_outputs(self) -> int:
        pass

    @abstractmethod
    def reset(self, rng_seed: int = None):
        pass

    @abstractmethod
    def step(self, brain_output: np.ndarray) -> Tuple[np.ndarray, Optional[Dict[str, np.ndarray]]]:
        pass


class DummyEnhancer(IEnhancer):
    """
    If no enhancer is used, this dummy enhancer simply passes through the predicted action from the brain to
    the environment. It does not compute anything.
    """

    def get_number_outputs(self) -> int:
        return 0

    def reset(self, rng_seed: int = None):
        pass

    def step(self, brain_output: np.ndarray) -> Tuple[np.ndarray, Optional[Dict[str, np.ndarray]]]:
        return brain_output, None
