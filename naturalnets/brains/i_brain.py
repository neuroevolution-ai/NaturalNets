import abc
from typing import Callable

import numpy as np
from attrs import define, field, validators
from scipy.special import expit

RELU_ACTIVATION = "relu"
TANH_ACTIVATION = "tanh"
LINEAR_ACTIVATION = "linear"


registered_brain_classes = {}


def get_brain_class(brain_class_name: str):
    if brain_class_name in registered_brain_classes:
        return registered_brain_classes[brain_class_name]
    else:
        raise RuntimeError(f"'{brain_class_name}' is not a valid brain. Please choose one from the following "
                           f"list: {list(registered_brain_classes)!r}")


def register_brain_class(brain_class):
    registered_brain_classes[brain_class.__name__] = brain_class
    return brain_class


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class IBrainCfg:
    type: str = field(validator=validators.instance_of(str))


class IBrain(abc.ABC):
    @abc.abstractmethod
    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: dict,
                 brain_state: dict):
        pass

    @abc.abstractmethod
    def step(self, u):
        pass

    @abc.abstractmethod
    def reset(self):
        pass

    @classmethod
    @abc.abstractmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):
        pass

    @classmethod
    @abc.abstractmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: dict):
        pass

    @classmethod
    @abc.abstractmethod
    def save_brain_state(cls, path, brain_state):
        pass

    @classmethod
    def load_brain_state(cls, path):
        # For Visualization usage
        pass

    @staticmethod
    def read_matrix_from_genome(individual: np.ndarray, index: int, matrix_rows: int, matrix_columns: int):
        matrix_size = matrix_columns * matrix_rows

        matrix = np.array(individual[index:index + matrix_size], dtype=np.single)
        matrix = matrix.reshape(matrix_rows, matrix_columns)

        index += matrix_size

        return matrix, index

    @classmethod
    def get_activation_function(cls, activation: str) -> Callable[[np.ndarray], np.ndarray]:

        if activation == RELU_ACTIVATION:
            return cls.relu
        elif activation == LINEAR_ACTIVATION:
            return cls.linear
        elif activation == TANH_ACTIVATION:
            return cls.tanh
        else:
            raise RuntimeError("The chosen activation function '{}' is not implemented".format(activation))

    @classmethod
    def get_individual_size(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict) -> int:
        """uses context information to calculate the required number of free parameter needed to construct
                an individual of this class"""

        def sum_dict(node):
            sum_ = 0
            for key, item in node.items():
                if isinstance(item, dict):
                    sum_ += sum_dict(item)
                else:
                    sum_ += item
            return sum_

        usage_dict = cls.get_free_parameter_usage(input_size, output_size, configuration, brain_state)
        return sum_dict(usage_dict)

    @staticmethod
    def relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    @staticmethod
    def linear(x: np.ndarray) -> np.ndarray:
        return x

    @staticmethod
    def tanh(x: np.ndarray) -> np.ndarray:
        return np.tanh(x)

    @staticmethod
    def sigmoid(x):
        return expit(x)
