import abc
import os
from typing import Callable, Type, Tuple, Optional, Dict

import numpy as np
from attrs import define, field, validators
from scipy.special import expit

from naturalnets.enhancers.i_enhancer import get_enhancer_class

RELU_ACTIVATION = "relu"
TANH_ACTIVATION = "tanh"
LINEAR_ACTIVATION = "linear"

# Keys to index the saved model for saving and loading
MODEL_FILE_NAME = "model.npz"
INDIVIDUAL_KEY = "individual"
BRAIN_STATE_KEY = "brain_state"
OB_MEAN_KEY = "ob_mean"
OB_STD_KEY = "ob_std"


registered_brain_classes = {}


def get_brain_class(brain_class_name: str) -> Type["IBrain"]:
    if brain_class_name in registered_brain_classes:
        return registered_brain_classes[brain_class_name]
    else:
        raise RuntimeError(f"'{brain_class_name}' is not a valid brain. Please choose one from the following "
                           f"list: {list(registered_brain_classes)!r}")


def register_brain_class(brain_class):
    registered_brain_classes[brain_class.__name__] = brain_class
    return brain_class


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class PreprocessingCfg:
    observation_standardization: bool = field(default=False, validator=validators.instance_of(bool))
    calc_ob_stat_prob: float = field(
        default=0.0,
        validator=[validators.instance_of(float), validators.ge(0.0), validators.le(1.0)]
    )

    observation_clipping: bool = field(default=False, validator=validators.instance_of(bool))
    ob_clipping_value: float = field(
        default=0.0,
        validator=[validators.instance_of(float), validators.ge(0.0)]
    )


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class IBrainCfg:
    type: str = field(validator=validators.instance_of(str))
    enhancer: dict
    preprocessing: dict = field(converter=lambda x: PreprocessingCfg(**x))


class IBrain(abc.ABC):
    @abc.abstractmethod
    def __init__(self, individual: np.ndarray, configuration: dict, brain_state: dict,
                 env_observation_size: int, env_action_size: int,
                 ob_mean: Optional[np.ndarray], ob_std: Optional[np.ndarray]):
        self.input_size, self.output_size = self.get_input_and_output_size(
            configuration=configuration,
            env_observation_size=env_observation_size,
            env_action_size=env_action_size
        )

        self.enhancer_class = get_enhancer_class(configuration["enhancer"]["type"])
        self.enhancer = self.enhancer_class(env_output_size=env_action_size)

        self.preprocessor_cfg = PreprocessingCfg(**configuration["preprocessing"])
        self.observation_standardization = self.preprocessor_cfg.observation_standardization
        self.calc_ob_stat_prob = self.preprocessor_cfg.calc_ob_stat_prob

        self.observation_clipping = self.preprocessor_cfg.observation_clipping
        self.ob_clipping_value = self.preprocessor_cfg.ob_clipping_value

        if self.observation_standardization:
            self.ob_mean = ob_mean
            self.ob_std = ob_std

    @abc.abstractmethod
    def internal_step(self, obs: np.ndarray) -> np.ndarray:
        pass

    def step(self, obs: np.ndarray) -> Tuple[np.ndarray, Optional[Dict[str, np.ndarray]]]:
        processed_obs = obs
        if self.observation_standardization:
            processed_obs = (processed_obs - self.ob_mean) / self.ob_std

        if self.observation_clipping:
            processed_obs = np.clip(processed_obs, -self.ob_clipping_value, +self.ob_clipping_value)

        action = self.internal_step(processed_obs)
        enhanced_action, enhancer_info = self.enhancer.step(action)

        return enhanced_action, enhancer_info

    @abc.abstractmethod
    def reset(self, rng_seed: int):
        self.enhancer.reset(rng_seed=rng_seed)

    @classmethod
    def get_input_and_output_size(cls, configuration: dict, env_observation_size: int,
                                  env_action_size: int) -> Tuple[int, int]:
        input_size = env_observation_size
        output_size = env_action_size

        enhancer_class = get_enhancer_class(configuration["enhancer"]["type"])
        enhancer = enhancer_class(env_action_size)
        output_size += enhancer.get_number_outputs()

        return input_size, output_size

    @classmethod
    @abc.abstractmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):
        pass

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: dict):
        return None

    @classmethod
    def register_brain_state_for_saving(cls, model_contents: dict,
                                        brain_state: Optional[Dict[str, np.ndarray]]) -> dict:
        return model_contents

    @classmethod
    def load_brain_state(cls, brain_data) -> Optional[Dict[str, np.ndarray]]:
        """
        For visualization purposes.

        :param brain_data: Is a NpzFile, i.e. a file loaded with np.load()
        :return: None or the brain_state
        """
        return None

    @classmethod
    def save_brain(cls, results_subdirectory: str, individual: np.ndarray, brain_state: Optional[dict] = None,
                   ob_mean: Optional[np.ndarray] = None, ob_std: Optional[np.ndarray] = None):
        file_name = os.path.join(results_subdirectory, MODEL_FILE_NAME)

        model_contents = {
            INDIVIDUAL_KEY: individual
        }

        model_contents = cls.register_brain_state_for_saving(model_contents, brain_state)

        if ob_mean is not None and ob_std is not None:
            model_contents[OB_MEAN_KEY] = ob_mean
            model_contents[OB_STD_KEY] = ob_std

        np.savez(file_name, **model_contents)

    @classmethod
    def load_brain(cls, path: str) -> Tuple[np.ndarray, Optional[dict], Optional[np.ndarray], Optional[np.ndarray]]:
        brain_data = np.load(path)

        individual = brain_data[INDIVIDUAL_KEY]

        brain_state = cls.load_brain_state(brain_data)

        ob_mean, ob_std = None, None
        if OB_MEAN_KEY in brain_data and OB_STD_KEY in brain_data:
            ob_mean = brain_data[OB_MEAN_KEY]
            ob_std = brain_data[OB_STD_KEY]

        return individual, brain_state, ob_mean, ob_std

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
