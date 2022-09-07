from typing import Dict

import pytest

from naturalnets.brains.i_layer_based_brain import ILayerBasedBrainCfg
from tests.brains.pytorch_brains import IPytorchBrainCfg


@pytest.fixture
def torch_config() -> IPytorchBrainCfg:
    return IPytorchBrainCfg(type="GRU_PyTorch", num_layers=3,
                            hidden_size=8,
                            use_bias=False)


@pytest.fixture
def brain_config() -> Dict:
    return {
        "type": "LSTM",
        "hidden_layer_structure": [2, 8, 16],
        "diagonal_hidden_to_hidden": False,
        "use_bias": False
    }


@pytest.fixture
def numpy_config() -> ILayerBasedBrainCfg:
    return ILayerBasedBrainCfg(type="GRULayered", hidden_layer_structure=[8, 8, 8], diagonal_hidden_to_hidden=False,
                               use_bias=False)
