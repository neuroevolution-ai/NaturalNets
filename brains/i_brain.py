import abc
import attr
import numpy as np

from typing import Callable


@attr.s(slots=True, auto_attribs=True, frozen=True)
class IBrainCfg(abc.ABC, dict):
    type: str


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

    @staticmethod
    def read_matrix_from_genome(individual: np.ndarray, index: int, matrix_rows: int, matrix_columns: int):
        matrix_size = matrix_columns * matrix_rows

        matrix = np.array(individual[index:index + matrix_size], dtype=np.single)
        matrix = matrix.reshape(matrix_rows, matrix_columns)

        index += matrix_size

        return matrix, index

    @classmethod
    def get_activation_function(cls, activation: str) -> Callable[[np.ndarray], np.ndarray]:

        if activation == "relu":
            return cls.relu
        elif activation == "linear":
            return cls.linear
        elif activation == "tanh":
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
        return 1 / (1 + np.exp(-x))
