import numpy as np
import tensorflow as tf
from tensorflow import keras

from naturalnets.brains.i_brain import IBrain
from naturalnets.brains.i_layer_based_brain import ILayerBasedBrainCfg


class TensorflowLSTM(IBrain):

    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: ILayerBasedBrainCfg,
                 brain_state: dict):
        self.configuration = configuration

        self.hidden = []
        self.lstm_layers = []

        input_shape = (1, 1, input_size)

        for i, hidden_size in enumerate(self.configuration.hidden_layer_structure):
            lstm_layer = keras.layers.LSTMCell(
                hidden_size,
                use_bias=self.configuration.use_bias
            )

            lstm_layer.trainable = False
            lstm_layer.build(input_shape=input_shape)

            input_shape = (1, 1, hidden_size)

            self.lstm_layers.append(lstm_layer)

            self.hidden.append([tf.zeros((1, hidden_size)), tf.zeros((1, hidden_size))])

        self.output_dense_layer = keras.layers.Dense(output_size, use_bias=False)
        self.output_dense_layer.trainable = False
        self.output_dense_layer.build(input_shape=(1, self.configuration.hidden_layer_structure[-1]))

        running_index = 0

        for i, layer in enumerate(self.lstm_layers):
            new_layer_weights = []

            for j, weight in enumerate(layer.get_weights()):

                weight_shape = weight.shape
                weight_num_elements = np.prod(weight_shape)

                weights = individual[running_index:running_index + weight_num_elements]

                if j < 2:
                    # Input to Hidden, and Hidden to Hidden weights
                    weights = weights.reshape(4, layer.units, weight.shape[0]).transpose(2, 0, 1).reshape(weight_shape)
                else:
                    # Bias
                    weights = weights.reshape(weight_shape)

                new_layer_weights.append(weights)

                running_index += weight_num_elements

            layer.set_weights(new_layer_weights)

        new_dense_layer_weights = []
        for weight in self.output_dense_layer.get_weights():
            weight_shape = weight.shape
            weight_num_elements = np.prod(weight_shape)

            new_weights = individual[running_index:running_index + weight_num_elements]
            new_weights = new_weights.reshape(output_size, -1).transpose(1, 0).reshape(weight_shape)
            new_dense_layer_weights.append(new_weights)

            running_index += weight_num_elements

        self.output_dense_layer.set_weights(new_dense_layer_weights)

        assert running_index == len(individual)

    def step(self, u: np.ndarray):
        output = tf.convert_to_tensor(u.reshape(1, -1))

        for i, lstm_layer in enumerate(self.lstm_layers):
            old_state_h, old_state_c = self.hidden[i]
            output, (state_h, state_c) = lstm_layer(output, states=[old_state_h, old_state_c])

            self.hidden[i] = [state_h, state_c]

        output = keras.activations.tanh(self.output_dense_layer(output))

        return output[0]

    def reset(self):
        raise NotImplementedError("This brain is only implemented to test the corresponding NumPy implementation, "
                                  "do not use it.")

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):
        raise NotImplementedError("This brain is only implemented to test the corresponding NumPy implementation, "
                                  "do not use it.")

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: dict):
        raise NotImplementedError("This brain is only implemented to test the corresponding NumPy implementation, "
                                  "do not use it.")

    @classmethod
    def save_brain_state(cls, path, brain_state):
        raise NotImplementedError("This brain is only implemented to test the corresponding NumPy implementation, "
                                  "do not use it.")
