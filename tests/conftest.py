from typing import Tuple

import pytest

from naturalnets.brains import IBrain
from naturalnets.brains.i_brain import get_brain_class

CTRNN_BRAIN = "CTRNN"
RNN_BRAIN = "RNN"
LSTM_BRAIN = "LSTM"
GRU_BRAIN = "GRU"
FF_BRAIN = "FeedForwardNN"

INPUT_SIZE = 30
OUTPUT_SIZE = 10


@pytest.fixture(
    params=[
        {"brain": brain} for brain in [CTRNN_BRAIN, RNN_BRAIN, LSTM_BRAIN, GRU_BRAIN, FF_BRAIN]
    ]
)
def brain_test_config(request) -> Tuple[int, int, dict, IBrain]:
    chosen_brain = request.param["brain"]

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
            "optimize_x0": True
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

    return INPUT_SIZE, OUTPUT_SIZE, brain_config, brain_class
