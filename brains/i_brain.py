import abc
import numpy as np

from typing import Callable


class IBrain(abc.ABC):

    @abc.abstractmethod
    def step(self, u):
        pass

    @abc.abstractmethod
    def reset(self):
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

    @staticmethod
    def relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    @staticmethod
    def linear(x: np.ndarray) -> np.ndarray:
        return x

    @staticmethod
    def tanh(x: np.ndarray) -> np.ndarray:
        return np.tanh(x)
