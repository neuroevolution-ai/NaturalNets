import itertools
from typing import Tuple, Type

import pytest

from naturalnets.brains import IBrain
from naturalnets.brains.i_brain import get_brain_class
from naturalnets.enhancers.i_enhancer import IEnhancer
from naturalnets.environments.i_environment import get_environment_class, IEnvironment

CTRNN_BRAIN = "CTRNN"
RNN_BRAIN = "RNN"
LSTM_BRAIN = "LSTM"
GRU_BRAIN = "GRU"
FF_BRAIN = "FeedForwardNN"

GUI_APP_ENV = "GUIApp"
MUJOCO_ENV = "GymMujoco"

NO_ENHANCER = None
RANDOM_ENHANCER = "RandomEnhancer"

INPUT_SIZE = 30
OUTPUT_SIZE = 10


@pytest.fixture
def reference_results_dir() -> str:
    return "tests/reference_results"


@pytest.fixture
def reference_results_file_name() -> str:
    return "reference_results.npz"


@pytest.fixture(
    params=[
        {"brain": brain} for brain in [CTRNN_BRAIN, RNN_BRAIN, LSTM_BRAIN, GRU_BRAIN, FF_BRAIN]
    ]
)
def brain_test_config(request) -> Tuple[int, int, dict, Type[IBrain]]:
    chosen_brain = request.param["brain"]
    brain_config, brain_class = _get_brain_config_and_class(chosen_brain)

    return INPUT_SIZE, OUTPUT_SIZE, brain_config, brain_class


@pytest.fixture(
    params=[
        {
            "brain": brain,
            "env": env,
            "enhancer": enhancer
        } for (brain, env, enhancer) in itertools.product(
            [CTRNN_BRAIN, RNN_BRAIN, LSTM_BRAIN, GRU_BRAIN, FF_BRAIN],
            [GUI_APP_ENV, MUJOCO_ENV],
            [NO_ENHANCER, RANDOM_ENHANCER]
        )
    ]
)
def ep_runner_test_config(request) -> Tuple[dict, Type[IBrain], dict, Type[IEnvironment], dict, Type[IEnhancer], dict]:
    chosen_brain = request.param["brain"]
    chosen_env = request.param["env"]
    chosen_enhancer = request.param["enhancer"]

    brain_config, brain_class = _get_brain_config_and_class(chosen_brain)
    env_config, env_class = _get_env_config_and_class(chosen_env)

    enhancer_config = {
        "type": chosen_enhancer
    }

    preprocessing_config = {
        "observation_standardization": False,
        "calc_ob_stat_prob": 0.0,
        "observation_clipping": False,
        "ob_clipping_value": 0.0
    }

    return brain_config, brain_class, env_config, env_class, enhancer_config, chosen_enhancer, preprocessing_config


def _get_brain_config_and_class(chosen_brain: str) -> Tuple[dict, Type[IBrain]]:
    if chosen_brain == CTRNN_BRAIN:
        brain_config = {
            "type": chosen_brain,
            "delta_t": 0.05,
            "differential_equation": "NaturalNet",
            "number_neurons": 5,
            "v_mask": "dense",
            "w_mask": "dense",
            "t_mask": "dense",
            "v_mask_density": 1.0,
            "w_mask_density": 1.0,
            "t_mask_density": 1.0,
            "clipping_range": 1.0,
            "set_principle_diagonal_elements_of_W_negative": True,
            "alpha": 0.0,
            "optimize_x0": False
        }
    elif chosen_brain == RNN_BRAIN or chosen_brain == LSTM_BRAIN or chosen_brain == GRU_BRAIN:
        brain_config = {
            "type": chosen_brain,
            "hidden_layers": [3, 5],
            "use_bias": True
        }
    elif chosen_brain == FF_BRAIN:
        brain_config = {
            "type": chosen_brain,
            "hidden_layers": [3, 5],
            "neuron_activation": "tanh",
            "neuron_activation_output": "tanh",
            "use_bias": True
        }
    else:
        raise AttributeError(f"Testing of '{chosen_brain}' is currently not implemented")

    brain_class = get_brain_class(chosen_brain)

    return brain_config, brain_class


def _get_env_config_and_class(chosen_env: str) -> Tuple[dict, Type[IEnvironment]]:
    if chosen_env == GUI_APP_ENV:
        env_config = {
            "type": GUI_APP_ENV,
            "number_time_steps": 200,
        }
    elif chosen_env == MUJOCO_ENV:
        env_config = {
            "type": chosen_env,
            "name": "Walker2d-v4"
        }
    else:
        raise AttributeError(f"Testing of '{chosen_env}' is currently not implemented")

    env_class = get_environment_class(chosen_env)

    return env_config, env_class
