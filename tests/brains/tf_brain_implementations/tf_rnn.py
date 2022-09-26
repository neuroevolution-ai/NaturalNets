import numpy as np
import tensorflow as tf
from tensorflow import keras

from naturalnets.brains.i_brain import IBrain
from naturalnets.brains.rnn import RNNConfig
from tests.brains.tf_brain_implementations.tf_brain_utils import assign_individual_to_tf_layer_weights


class TensorflowRNN(IBrain):

    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: RNNConfig,
                 brain_state: dict):
        self.configuration = configuration

        self.hidden = []
        self.rnn_layers = []

        input_shape = (1, 1, input_size)

        for i, hidden_size in enumerate(self.configuration.hidden_layers):
            rnn_layer = keras.layers.SimpleRNNCell(
                hidden_size,
                use_bias=self.configuration.use_bias
            )

            rnn_layer.trainable = False
            rnn_layer.build(input_shape=input_shape)

            input_shape = (1, 1, hidden_size)

            self.rnn_layers.append(rnn_layer)

            self.hidden.append(tf.zeros((1, hidden_size)))

        self.output_dense_layer = keras.layers.Dense(output_size, use_bias=self.configuration.use_bias)
        self.output_dense_layer.trainable = False
        self.output_dense_layer.build(input_shape=(1, self.configuration.hidden_layers[-1]))

        assign_individual_to_tf_layer_weights(
            individual,
            input_size=input_size,
            output_size=output_size,
            number_of_gates=1,
            hidden_layers=self.configuration.hidden_layers,
            lstm_layers=self.rnn_layers,
            output_dense_layer=self.output_dense_layer
        )

    def step(self, u: np.ndarray):
        output = tf.convert_to_tensor(u.reshape(1, -1))

        for i, lstm_layer in enumerate(self.rnn_layers):
            output, (state_h) = lstm_layer(output, states=[self.hidden[i]], training=False)

            self.hidden[i] = state_h[0]

        output = keras.activations.tanh(self.output_dense_layer(output, training=False))

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
