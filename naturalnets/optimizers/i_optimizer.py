import abc
from typing import List

import numpy as np
from attrs import define, field, validators

registered_optimizer_classes = {}


def get_optimizer_class(optimizer_class_name: str):
    if optimizer_class_name in registered_optimizer_classes:
        return registered_optimizer_classes[optimizer_class_name]
    else:
        raise RuntimeError(f"'{optimizer_class_name}' is not a valid optimizer. Please choose one from the following "
                           f"list: {list(registered_optimizer_classes)!r}")


def register_optimizer_class(optimizer_class):
    registered_optimizer_classes[optimizer_class.__name__] = optimizer_class
    return optimizer_class


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class IOptimizerCfg:
    type: str = field(validator=validators.instance_of(str))


class IOptimizer(abc.ABC):

    def __init__(self, individual_size: int, global_seed: int, configuration: dict, **kwargs):
        self.individual_size = individual_size
        self.global_seed = global_seed
        self.config_dict = configuration

    @abc.abstractmethod
    def ask(self):
        pass

    @abc.abstractmethod
    def tell(self, rewards: List[float]) -> np.ndarray:
        pass
