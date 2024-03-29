from typing import List, Tuple

import numpy as np
from attrs import define, field, validators

from naturalnets.brains.brain_utils import assign_individual_to_brain_weights, validate_list_of_ints_larger_zero
from naturalnets.brains.i_brain import register_brain_class, IBrain, IBrainCfg


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class GRUConfig(IBrainCfg):
    hidden_layers: List[int] = field(validator=validate_list_of_ints_larger_zero)
    use_bias: bool = field(validator=validators.instance_of(bool))


@register_brain_class
class GRU(IBrain):
    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: dict,
                 brain_state: dict):
        super().__init__(input_size, output_size, individual, configuration, brain_state)

        if isinstance(configuration, dict):
            self.configuration = GRUConfig(**configuration)
        else:
            self.configuration = configuration

        brain_weights = assign_individual_to_brain_weights(
            individual,
            input_size=self.input_size,
            output_size=self.output_size,
            number_of_gates=3,
            hidden_layers=self.configuration.hidden_layers,
            use_bias=self.configuration.use_bias
        )

        self.weights_input_to_hidden = brain_weights[0]
        self.weights_hidden_to_hidden = brain_weights[1]
        self.biases = brain_weights[2]
        self.weights_hidden_to_output = brain_weights[3]
        self.output_bias = brain_weights[4]

        self.hidden = []

        for hidden_size in self.configuration.hidden_layers:
            self.hidden.append(
                np.zeros(hidden_size, dtype=np.float32)
            )

    def step(self, inputs: np.ndarray) -> np.ndarray:
        current_input = inputs
        for i in range(len(self.configuration.hidden_layers)):
            w_ih = self.weights_input_to_hidden[i]
            b_ih = self.biases[i]
            w_hh = self.weights_hidden_to_hidden[i]
            h_old = self.hidden[i]

            z_t = self.sigmoid(
                np.dot(w_ih[0], current_input)
                + b_ih[0]
                + np.dot(w_hh[0], h_old)
            )

            r_t = self.sigmoid(
                np.dot(w_ih[1], current_input)
                + b_ih[1]
                + np.dot(w_hh[1], h_old)
            )

            # Note that r_t is multiplied with the old hidden state _before_ the matrix multiplication. Other
            # implementations might do this after the matmul. I chose to do it this way, because in the most recent
            # version of the GRU paper the authors do the same. In addition, the corresponding TensorFlow variant
            # (GRUCell with reset_after=False), only requires one bias, instead of two when setting reset_after=True.
            # Read more here: https://www.tensorflow.org/api_docs/python/tf/keras/layers/GRU#used-in-the-notebooks
            hh = np.tanh(
                np.dot(w_ih[2], current_input)
                + b_ih[2]
                + np.dot(w_hh[2], r_t * h_old)
            )

            h_new = z_t * h_old + (1 - z_t) * hh

            self.hidden[i] = h_new
            current_input = h_new

        return np.tanh(np.dot(self.weights_hidden_to_output, current_input) + self.output_bias)

    def reset(self):
        self.hidden = []
        for hidden_size in self.configuration.hidden_layers:
            self.hidden.append(
                np.zeros(hidden_size, dtype=np.float32)
            )

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict,
                                 brain_state: dict) -> Tuple[dict, int, int]:
        individual_size = 0
        parameter_dict = {}

        config = GRUConfig(**configuration)
        current_input_size = input_size

        for i, hidden_size in enumerate(config.hidden_layers):
            input_to_hidden_size = current_input_size * hidden_size * 3
            hidden_to_hidden_size = hidden_size * hidden_size * 3

            layer_dict = {
                "number_weights_input_to_hidden": input_to_hidden_size,
                "number_weights_hidden_to_hidden": hidden_to_hidden_size
            }

            individual_size += (input_to_hidden_size + hidden_to_hidden_size)

            if config.use_bias:
                layer_dict["number_of_biases"] = hidden_size * 3
                individual_size += hidden_size * 3

            parameter_dict[f"gru_layer_{i}"] = layer_dict

            current_input_size = hidden_size

        output_neurons_start_index = individual_size

        output_layer_size = current_input_size * output_size
        output_layer_dict = {
            "number_output_weights": output_layer_size
        }

        individual_size += output_layer_size

        if config.use_bias:
            output_layer_dict["output_biases"] = output_size
            individual_size += output_size

        output_neurons_end_index = individual_size
        parameter_dict["output_layer"] = output_layer_dict

        return parameter_dict, output_neurons_start_index, output_neurons_end_index
