from typing import List

import numpy as np
from tensorflow import keras


def assign_individual_to_tf_layer_weights(individual: np.ndarray, input_size: int, output_size: int,
                                          number_of_gates: int, hidden_layers: List[int],
                                          lstm_layers: List[keras.layers.Layer],
                                          output_dense_layer: keras.layers.Layer):
    running_index = 0
    current_input_size = input_size
    for i, layer in enumerate(lstm_layers):
        hidden_size = hidden_layers[i]
        new_layer_weights = []

        for j, weight in enumerate(layer.get_weights()):

            weight_shape = weight.shape
            weight_num_elements = np.prod(weight_shape)

            weights = individual[running_index:running_index + weight_num_elements]

            if j == 0:
                # Input to Hidden weights
                # Reshape the part of the individual array to match our implementation, then
                # transpose and reshape to match the TensorFlow implementation.
                # This ensures that the weights between the two implementations are equal.
                weights = weights.reshape(number_of_gates, hidden_size, current_input_size)
                weights = weights.transpose(2, 0, 1).reshape(current_input_size, -1)
            elif j == 1:
                # Hidden to Hidden weights
                # Same procedure as above.
                weights = weights.reshape(number_of_gates, hidden_size, hidden_size)
                weights = weights.transpose(2, 0, 1).reshape(hidden_size, -1)
            else:
                # Bias
                weights = weights.reshape(weight_shape)

            new_layer_weights.append(weights)

            running_index += weight_num_elements

        layer.set_weights(new_layer_weights)
        current_input_size = hidden_size

    new_dense_layer_weights = []
    for weight in output_dense_layer.get_weights():
        weight_shape = weight.shape
        weight_num_elements = np.prod(weight_shape)

        new_weights = individual[running_index:running_index + weight_num_elements]
        new_weights = new_weights.reshape(output_size, -1).transpose(1, 0).reshape(weight_shape)
        new_dense_layer_weights.append(new_weights)

        running_index += weight_num_elements

    output_dense_layer.set_weights(new_dense_layer_weights)

    assert running_index == len(individual)
