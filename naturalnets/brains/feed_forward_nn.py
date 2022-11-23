import itertools
from typing import List, Tuple

import numpy as np
from attrs import define, field, validators

from naturalnets.brains.brain_utils import validate_list_of_ints_larger_zero
from naturalnets.brains.i_brain import (IBrain, IBrainCfg, register_brain_class, LINEAR_ACTIVATION, RELU_ACTIVATION,
                                        TANH_ACTIVATION)


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class FeedForwardCfg(IBrainCfg):
    hidden_layers: List[int] = field(validator=validate_list_of_ints_larger_zero)
    neuron_activation: str = field(
        validator=[validators.instance_of(str), validators.in_([LINEAR_ACTIVATION, TANH_ACTIVATION, RELU_ACTIVATION])]
    )
    neuron_activation_output: str = field(
        validator=[validators.instance_of(str), validators.in_([TANH_ACTIVATION])]
    )
    use_bias: bool = field(validator=validators.instance_of(bool))


@register_brain_class
class FeedForwardNN(IBrain):

    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: dict,
                 brain_state: dict):
        super().__init__(input_size, output_size, individual, configuration, brain_state)

        self.config = FeedForwardCfg(**configuration)

        # Set activation functions for hidden layers and output layer based on config
        self.activation_hidden_layers = self.get_activation_function(self.config.neuron_activation)

        assert self.config.neuron_activation_output == "tanh", ("The output activation function must be 'tanh', "
                                                                "because we require that brains output values in the "
                                                                "[-1, 1] range.")

        self.activation_output_layer = self.get_activation_function(self.config.neuron_activation_output)

        self.weights_hidden_layers: List[np.ndarray] = []
        self.biases_hidden_layers: List[np.ndarray] = []

        index = 0
        previous_layer_size = self.input_size

        # Read out weight matrices and bias matrices from genome for hidden layers
        for hidden_layer in self.config.hidden_layers:
            current_weight, index = self.read_matrix_from_genome(individual, index, hidden_layer, previous_layer_size)
            self.weights_hidden_layers.append(current_weight)

            if self.config.use_bias:
                current_bias, index = self.read_matrix_from_genome(individual, index, hidden_layer, 1)
                self.biases_hidden_layers.append(current_bias)

            previous_layer_size = hidden_layer

        # Read out weight matrix from genome for output layer
        self.weights_output_layer, index = self.read_matrix_from_genome(individual, index, self.output_size,
                                                                        previous_layer_size)

        # Read out bias matrix from genome for output layer
        if self.config.use_bias:
            self.biases_output_layer, index = self.read_matrix_from_genome(individual, index, self.output_size, 1)

    def step(self, ob: np.ndarray) -> np.ndarray:

        assert ob.ndim == 1
        assert ob.size == self.input_size

        x = self.predict(ob.reshape(ob.size, 1))

        return x.flatten()

    def reset(self):
        pass

    def predict(self, ob: np.ndarray) -> np.ndarray:

        assert ob.ndim > 1
        assert ob.shape[-2] == self.input_size
        assert ob.shape[-1] == 1

        x = ob

        # Calculate hidden layers
        # Note: itertools.zip_longest is necessary here instead of zip, since self.biases_hidden_layers is
        # an empty list, if self.use_bias is False
        for weights, biases in itertools.zip_longest(self.weights_hidden_layers, self.biases_hidden_layers):
            x = np.matmul(weights, x)
            if self.config.use_bias:
                x = np.add(x, biases)
            x = self.activation_hidden_layers(x)

        # Calculate output layer
        x = np.matmul(self.weights_output_layer, x)
        if self.config.use_bias:
            x = np.add(x, self.biases_output_layer)
        x = self.activation_output_layer(x)

        return x

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict,
                                 brain_state: dict) -> Tuple[dict, int, int]:

        config = FeedForwardCfg(**configuration)

        individual_size = 0
        last_layer = input_size

        for hidden_layer in config.hidden_layers:
            individual_size += last_layer * hidden_layer
            last_layer = hidden_layer

        output_neurons_start_index = individual_size

        output_matrix_size = last_layer * output_size
        individual_size += output_matrix_size

        output_neurons_end_index = individual_size

        if config.use_bias:
            individual_size += sum(config.hidden_layers) + output_size

            # Subtract output bias size and output matrix size from the end index
            output_neurons_start_index = individual_size - output_size - output_matrix_size
            output_neurons_end_index = individual_size

        return {"individual_size": individual_size}, output_neurons_start_index, output_neurons_end_index
