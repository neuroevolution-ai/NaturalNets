from typing import Dict, List

import pytest


@pytest.fixture
def tensorflow_cmp_configs() -> List[Dict]:
    return [
        {
            "type": "RNN",
            "hidden_layers": [2, 4, 8],
            "use_bias": False
        },
        {
            "type": "RNN",
            "hidden_layers": [2, 4, 8],
            "use_bias": True
        },
        {
            "type": "RNN",
            "hidden_layers": [16],
            "use_bias": False
        },
        {
            "type": "RNN",
            "hidden_layers": [16],
            "use_bias": True
        },
        {
            "type": "LSTM",
            "hidden_layers": [2, 4, 8],
            "use_bias": False
        },
        {
            "type": "LSTM",
            "hidden_layers": [2, 4, 8],
            "use_bias": True
        },
        {
            "type": "LSTM",
            "hidden_layers": [16],
            "use_bias": False
        },
        {
            "type": "LSTM",
            "hidden_layers": [16],
            "use_bias": True
        },
        {
            "type": "GRU",
            "hidden_layers": [2, 4, 8],
            "use_bias": False
        },
        {
            "type": "GRU",
            "hidden_layers": [2, 4, 8],
            "use_bias": True
        },
        {
            "type": "GRU",
            "hidden_layers": [16],
            "use_bias": False
        },
        {
            "type": "GRU",
            "hidden_layers": [16],
            "use_bias": True
        }
    ]
