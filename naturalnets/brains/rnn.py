from typing import List, Union, Dict

import attrs
import numpy as np

from naturalnets.brains.brain_utils import assign_individual_to_brain_weights
from naturalnets.brains.i_brain import register_brain_class
from naturalnets.brains import IBrain


@attrs.define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class RNNConfig:
    type: str
    hidden_layers: List[int]
    use_bias: bool


@register_brain_class
class RNN(IBrain):
    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: Union[RNNConfig, Dict],
                 brain_state: dict):
        if isinstance(configuration, dict):
            self.configuration = RNNConfig(**configuration)
        else:
            self.configuration = configuration

        brain_weights = assign_individual_to_brain_weights(
            individual,
            input_size=input_size,
            output_size=output_size,
            number_of_gates=1,
            hidden_layers=self.configuration.hidden_layers,
            use_bias=self.configuration.use_bias
        )

        self.weights_input_to_hidden = [x[0] for x in brain_weights[0]]
        self.weights_hidden_to_hidden = [x[0] for x in brain_weights[1]]
        self.biases = [x[0] for x in brain_weights[2]]
        self.weights_hidden_to_output = brain_weights[3]
        self.output_bias = brain_weights[4]

        self.hidden = []

        for hidden_size in self.configuration.hidden_layers:
            self.hidden.append(
                np.zeros(hidden_size, dtype=np.float32)
            )

    def step(self, inputs: np.ndarray):
        current_input = inputs
        for i in range(len(self.configuration.hidden_layers)):
            w_ih = self.weights_input_to_hidden[i]
            b_ih = self.biases[i]
            w_hh = self.weights_hidden_to_hidden[i]
            h_old = self.hidden[i]

            h_new = np.tanh(
                np.dot(w_ih, current_input)
                + b_ih
                + np.dot(w_hh, h_old)
            )

            self.hidden[i] = h_new
            current_input = h_new

        return np.tanh(np.dot(self.weights_hidden_to_output, current_input) + self.output_bias)

    def reset(self):
        self.hidden = []
        for hidden_size in self.configuration.hidden_layers:
            self.hidden.append(
                np.zeros(hidden_size, dtype=np.float32),
            )

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):
        parameter_dict = {}

        config = RNNConfig(**configuration)
        current_input_size = input_size

        for i, hidden_size in enumerate(config.hidden_layers):
            layer_dict = {
                "number_weights_input_to_hidden": current_input_size * hidden_size,
                "number_weights_hidden_to_hidden": hidden_size * hidden_size
            }

            if config.use_bias:
                layer_dict["number_of_biases"] = hidden_size

            parameter_dict[f"lstm_layer_{i}"] = layer_dict

            current_input_size = hidden_size

        output_layer_dict = {
            "number_output_weights": current_input_size * output_size
        }

        if config.use_bias:
            output_layer_dict["output_biases"] = output_size

        parameter_dict["output_layer"] = output_layer_dict

        return parameter_dict

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: dict):
        pass

    @classmethod
    def save_brain_state(cls, path, brain_state):
        pass