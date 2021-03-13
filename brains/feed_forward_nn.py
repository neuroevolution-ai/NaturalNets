from brains.i_brain import IBrain

import attr
import itertools
import numpy as np
from typing import List


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class FeedForwardCfg:
    type: str
    hidden_layers: List[int]
    neuron_activation: str
    neuron_activation_output: str
    use_bias: bool


class FeedForwardNN(IBrain):

    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: dict,
                 brain_state: dict):

        self.config = FeedForwardCfg(**configuration)

        assert len(individual) == self.get_individual_size(input_size, output_size, configuration, brain_state)

        self.input_size: int = input_size
        self.output_size: int = output_size

        # Set activation functions for hidden layers and output layer based on config
        self.activation_hidden_layers = self.get_activation_function(self.config.neuron_activation)
        self.activation_output_layer = self.get_activation_function(self.config.neuron_activation_output)

        self.weights_hidden_layers: List[np.ndarray] = []
        self.biases_hidden_layers: List[np.ndarray] = []

        index = 0
        previous_layer_size = self.input_size

        # Read out weight matrizes and bias matrizes from genome for hidden layers
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
    def generate_brain_state(cls, number_inputs: int, number_outputs: int, configuration: dict):
        return None

    @classmethod
    def load_brain_state(cls, path):
        pass

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):

        config = FeedForwardCfg(**configuration)

        individual_size = 0
        last_layer = input_size

        for hidden_layer in config.hidden_layers:
            individual_size += last_layer * hidden_layer
            last_layer = hidden_layer

        individual_size += last_layer * output_size

        if config.use_bias:
            individual_size += sum(config.hidden_layers) + output_size

        return {'individual_size': individual_size}

    @classmethod
    def get_individual_size(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):

        individual_size = 0
        free_parameter_usage = cls.get_free_parameter_usage(input_size, output_size, configuration, brain_state)

        for free_parameters in free_parameter_usage.values():
            individual_size += free_parameters

        return individual_size
