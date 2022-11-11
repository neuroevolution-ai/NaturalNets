import itertools
from typing import Tuple

import pytest

CTRNN_BRAIN = "CTRNN"
RNN_BRAIN = "RNN"
LSTM_BRAIN = "LSTM"
GRU_BRAIN = "GRU"

CMA_ES_OPTIMIZER = "CmaEsDeap"

NO_ENHANCER = None
RANDOM_ENHANCER = "RandomEnhancer"


# Pair-match all brains and optimizer, so that each possible pair is tested
@pytest.fixture(
    params=[
        {
            "brain": brain,
            "optimizer": optimizer,
            "enhancer": enhancer
        } for (brain, optimizer, enhancer) in itertools.product(
            [CTRNN_BRAIN, RNN_BRAIN, LSTM_BRAIN, GRU_BRAIN],
            [CMA_ES_OPTIMIZER],
            [NO_ENHANCER, RANDOM_ENHANCER]
        )
    ]
)
def train_config(request) -> Tuple[dict, str, str, str]:
    chosen_brain = request.param["brain"]
    chosen_optimizer = request.param["optimizer"]
    chosen_enhancer = request.param["enhancer"]

    train_config = {
        "number_generations": 3,
        "number_validation_runs": 5,
        "number_rounds": 3,
        "maximum_env_seed": 100000,
        "global_seed": 0,
        "environment": {
            "type": "GymMujoco",
            "name": "InvertedPendulum-v4"
        }
    }

    if chosen_brain == CTRNN_BRAIN:
        train_config["brain"] = {
            "type": CTRNN_BRAIN,
            "delta_t": 0.05,
            "differential_equation": "NaturalNet",
            "number_neurons": 2,
            "v_mask": "dense",
            "w_mask": "dense",
            "t_mask": "dense",
            "v_mask_density": 1.0,
            "w_mask_density": 1.0,
            "t_mask_density": 1.0,
            "clipping_range": 1.0,
            "set_principle_diagonal_elements_of_W_negative": True,
            "alpha": 0.0,
            "optimize_x0": True
        }
    elif chosen_brain == RNN_BRAIN or chosen_brain == LSTM_BRAIN or chosen_brain == GRU_BRAIN:
        train_config["brain"] = {
            "type": chosen_brain,
            "hidden_layers": [2],
            "use_bias": True
        }
    else:
        raise AttributeError(f"Brain '{chosen_brain}' cannot be used to configure the training config")

    if chosen_optimizer == CMA_ES_OPTIMIZER:
        train_config["optimizer"] = {
            "type": "CmaEsDeap",
            "population_size": 20,
            "sigma": 1.0
        }
    else:
        raise AttributeError(f"Optimizer '{chosen_optimizer}' cannot be used to configure the training config")

    if chosen_enhancer != NO_ENHANCER and chosen_enhancer != RANDOM_ENHANCER:
        raise AttributeError(f"Enhancer '{chosen_enhancer}' cannot be used to configure the training config")

    # Currently the enhancers do not have any additional parameters, so we can simply do this:
    train_config["enhancer"] = {
        "type": chosen_enhancer
    }

    return train_config, chosen_brain, chosen_optimizer, str(chosen_enhancer)
