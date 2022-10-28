from typing import List

import numpy as np


def assign_individual_to_brain_weights(individual: np.ndarray, input_size: int, output_size: int, number_of_gates: int,
                                       hidden_layers: List[int], use_bias: bool):
    weights_input_to_hidden = []
    weights_hidden_to_hidden = []
    biases = []

    current_index = 0
    current_input_size = input_size
    for i, hidden_size in enumerate(hidden_layers):
        num_elements = number_of_gates * current_input_size * hidden_size

        weight_ih = individual[current_index:current_index + num_elements]
        weights_input_to_hidden.append(weight_ih.reshape(number_of_gates, hidden_size, current_input_size))

        current_index += num_elements

        num_elements = number_of_gates * hidden_size * hidden_size

        weight_hh = individual[current_index:current_index + num_elements]
        weights_hidden_to_hidden.append(weight_hh.reshape(number_of_gates, hidden_size, hidden_size))

        current_index += num_elements

        if use_bias:
            num_elements = number_of_gates * hidden_size

            bias = individual[current_index:current_index + num_elements]
            biases.append(bias.reshape(number_of_gates, hidden_size))

            current_index += num_elements
        else:
            # No bias, simply use zeros as they are added and do not alter the output
            biases.append(np.zeros((number_of_gates, hidden_size)))

        current_input_size = hidden_size

    num_elements = current_input_size * output_size

    weight_ho = individual[current_index:current_index + num_elements]
    weights_hidden_to_output = weight_ho.reshape(output_size, current_input_size)

    current_index += num_elements

    if use_bias:
        output_bias = individual[current_index:current_index + output_size]

        current_index += output_size
    else:
        output_bias = np.zeros((output_size,))

    assert current_index == len(individual)

    return weights_input_to_hidden, weights_hidden_to_hidden, biases, weights_hidden_to_output, output_bias


def validate_list_of_ints_larger_zero(instance, attribute, value):
    """
    A custom attrs validator, to validate that value is a list of integers
    """
    if isinstance(value, list):
        validate_failed = not all(isinstance(x, int) and x > 0 for x in value)
    else:
        validate_failed = True

    if validate_failed:
        raise ValueError(f"'{attribute.name}' must be a list of integers larger than 0")
