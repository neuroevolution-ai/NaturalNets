import abc
from typing import List

import attr
import numpy as np

from naturalnets.brains.i_brain import IBrain, IBrainCfg


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class ILayerBasedBrainCfg(IBrainCfg):
    # The structure of the layers
    # Each list entry translates to the size of one layer
    # The layers are in the given order
    hidden_layer_structure: List[int]
    # Whether a neuron can only use its own state form the last timestep
    diagonal_hidden_to_hidden: bool = False
    use_bias: bool = False


class ILayerBasedBrain(IBrain, abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def layer_step(layer_input: np.ndarray, weight_ih, weight_hh, bias_h, hidden):
        # Compute one layer step
        pass

    @staticmethod
    @abc.abstractmethod
    def get_number_gates():
        # How many Gates are used in the specific network?
        # Haw many matrices are needed for each layer to calculate the next state and output value
        pass

    @staticmethod
    @abc.abstractmethod
    def get_number_hidden_values():
        # How many hidden values are used in one cell
        pass

    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: ILayerBasedBrainCfg,
                 brain_state: dict):
        if not type(configuration) is ILayerBasedBrainCfg:
            configuration = ILayerBasedBrainCfg(**configuration)
        hidden_layer_structure: List[int] = configuration.hidden_layer_structure

        # initialize weights out of individual

        individual_index = 0  # progress index
        # initialize empty
        self.weight_ih = []  # Weights for weighted input values
        self.weight_hh = []  # Weights for weighted stored values
        self.bias_h = []  # Biases
        self.hidden = []  # Initial values for state storage
        self.layer_output = []  # Weights from output last Layer to output nodes
        number_gates = self.get_number_gates()
        number_hidden_values = self.get_number_hidden_values()

        # iterate for all given layers in the structure
        for layer in range(len(hidden_layer_structure)):

            # Matrices for weighted input values in calculations
            layer_input_size = input_size if layer == 0 else hidden_layer_structure[layer - 1]
            number_elements = number_gates * hidden_layer_structure[layer] * layer_input_size
            self.weight_ih.append(
                np.array(
                    individual[individual_index: individual_index + number_elements]
                ).reshape((number_gates, hidden_layer_structure[layer], layer_input_size))
            )
            individual_index += number_elements

            # Matrices for weighted state values in calculations
            if configuration.diagonal_hidden_to_hidden:  # Whether each neuron can only access its own state
                self.weight_hh.append(
                    [np.diag(individual[
                             individual_index + k * hidden_layer_structure[layer]:
                             individual_index + k * hidden_layer_structure[layer] + hidden_layer_structure[layer]
                             ])
                     for k in range(number_gates)
                     ]
                )
                individual_index += number_gates * hidden_layer_structure[layer]
            else:
                number_elements = number_gates * hidden_layer_structure[layer] * hidden_layer_structure[layer]
                self.weight_hh.append(
                    np.array(
                        individual[individual_index: individual_index + number_elements]
                    ).reshape((number_gates, hidden_layer_structure[layer], hidden_layer_structure[layer]))
                )
                individual_index += number_elements

            # initialize biases

            # Biases for gates
            if configuration.use_bias:
                number_elements = hidden_layer_structure[layer] * number_gates
                self.bias_h.append(
                    np.array(
                        individual[individual_index: individual_index + number_elements]
                    ).reshape((number_gates, hidden_layer_structure[layer]))
                )
                individual_index += number_elements
            else:
                self.bias_h.append(np.zeros((number_gates, hidden_layer_structure[layer])).astype(np.float32))

            # initialize initial state values
            self.hidden.append(np.zeros((number_hidden_values, hidden_layer_structure[layer])))

            self.layer_output.append(np.zeros((hidden_layer_structure[layer])))
        # for end

        # Matrix for transforming output of last layer into output neurons
        number_elements = hidden_layer_structure[len(hidden_layer_structure) - 1] * output_size
        self.weight_ho = np.array(
            individual[individual_index: individual_index + number_elements]
        ).reshape((output_size, hidden_layer_structure[len(hidden_layer_structure) - 1]))
        individual_index += number_elements

        # If all values have been used, get_individual_size() should provide the correct number
        assert individual_index == len(individual)

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):

        configuration = ILayerBasedBrainCfg(**configuration)
        number_gates = cls.get_number_gates()
        hidden_size = cls.get_number_hidden_values()
        hidden_structure = configuration.hidden_layer_structure
        individuals = {}

        for layer in range(len(hidden_structure)):
            layer_dict = {
                # Matrices for weighted input values
                # The first Layer don't has an output from the previous layer, but the input values
                "input_weight_matrix": number_gates * hidden_structure[layer] * (
                    input_size if layer == 0 else hidden_structure[layer - 1]),
                # Matrices for weighted state values
                "hidden_weight_matrix": number_gates * hidden_structure[layer] * (
                    1 if configuration.diagonal_hidden_to_hidden else hidden_structure[layer])
            }
            # initialize biases
            if configuration.use_bias:
                layer_dict["bias"] = hidden_structure[layer] * number_gates

            individuals["layer " + str(layer)] = layer_dict
        # for end

        # Matrix for transforming output of last layer into output neurons
        individuals["output_weight_matrix"] = hidden_structure[len(hidden_structure) - 1] * output_size
        return individuals

    def step(self, ob: np.ndarray):
        layer_input = ob
        # iterate for all given layers
        for layer in range(len(self.hidden)):
            if layer == 0:
                x = layer_input
            else:
                x = self.layer_output[layer - 1]
            # Returns a list with two elements.
            # The first element is the calculated new hidden cell state, the second is the layer output
            # Necessary for LSTM
            layer_result = self.layer_step(x, self.weight_ih[layer], self.weight_hh[layer], self.bias_h[layer],
                                           self.hidden[layer])
            self.hidden[layer] = layer_result[0]
            self.layer_output[layer] = layer_result[1]
        return np.tanh(np.dot(self.weight_ho, self.layer_output[len(self.layer_output) - 1]))

    def reset(self):
        self.hidden = np.zeros_like(self.hidden)

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: dict):
        pass

    @classmethod
    def save_brain_state(cls, path, brain_state):
        pass
