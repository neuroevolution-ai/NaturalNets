import itertools

import pytest


@pytest.fixture(
    params=[
        {
            "brain": brain,
            "hidden_layers": hidden_layers,
            "use_bias": use_bias
        } for (brain, hidden_layers, use_bias) in itertools.product(
            ["RNN", "LSTM", "GRU"],
            [[2, 4, 8], [16]],
            [True, False]
        )
    ]
)
def tensorflow_cmp_config(request) -> dict:
    chosen_brain = request.param["brain"]
    chosen_hidden_layers = request.param["hidden_layers"]
    chosen_use_bias = request.param["use_bias"]

    config = {
        "type": chosen_brain,
        "hidden_layers": chosen_hidden_layers,
        "use_bias": chosen_use_bias
    }

    return config
