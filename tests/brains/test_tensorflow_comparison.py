import time

from typing import Dict, List

import numpy as np
import tensorflow as tf

from naturalnets.brains import LSTM, GRU, RNN
from naturalnets.brains.gru import GRUConfig
from naturalnets.brains.lstm import LSTMConfig
from naturalnets.brains.rnn import RNNConfig
from tests.brains.tf_brain_implementations.tf_gru import TensorflowGRU
from tests.brains.tf_brain_implementations.tf_lstm import TensorflowLSTM
from tests.brains.tf_brain_implementations.tf_rnn import TensorflowRNN

INPUT_SIZE = 28
OUTPUT_SIZE = 8
NUMBER_INPUTS = 1000


def get_rnn_implementations(brain_configuration, input_size, output_size):
    if brain_configuration["type"] == "LSTM":
        individual_size = LSTM.get_individual_size(input_size, output_size, brain_configuration, {})

        config = LSTMConfig(**brain_configuration)

        our_implementation_class = LSTM
        tf_implementation_class = TensorflowLSTM
    elif brain_configuration["type"] == "GRU":
        individual_size = GRU.get_individual_size(input_size, output_size, brain_configuration, {})

        config = GRUConfig(**brain_configuration)

        our_implementation_class = GRU
        tf_implementation_class = TensorflowGRU
    elif brain_configuration["type"] == "RNN":
        individual_size = RNN.get_individual_size(input_size, output_size, brain_configuration, {})

        config = RNNConfig(**brain_configuration)

        our_implementation_class = RNN
        tf_implementation_class = TensorflowRNN
    else:
        raise RuntimeError(f"Unsupported rnn_type '{brain_configuration['type']}'")

    # Make two copies to avoid possible errors due to TensorFlow reusing data from the same memory address
    individual_tensorflow = np.random.randn(individual_size).astype(np.float32)
    individual_ours = np.copy(individual_tensorflow)

    tf_implementation = tf_implementation_class(
        input_size,
        output_size,
        individual=individual_tensorflow,
        configuration=config,
        brain_state={}
    )

    our_implementation = our_implementation_class(
        input_size,
        output_size,
        individual=individual_ours,
        configuration=config,
        brain_state={}
    )

    tf_hidden_state = np.random.randn(np.sum(config.hidden_layers)).astype(np.float32)
    tf_cell_state = np.random.randn(np.sum(config.hidden_layers)).astype(np.float32)

    our_hidden_state = np.copy(tf_hidden_state)
    our_cell_state = np.copy(tf_cell_state)

    if brain_configuration["type"] == "LSTM":
        current_index = 0
        for i, hidden_units in enumerate(config.hidden_layers):
            tf_implementation.hidden[i] = [
                tf.convert_to_tensor(
                    tf_hidden_state[current_index:current_index + hidden_units].reshape((1, hidden_units))
                ),
                tf.convert_to_tensor(
                    tf_cell_state[current_index:current_index + hidden_units].reshape((1, hidden_units))
                )
            ]

            current_index += hidden_units

        assert current_index == len(tf_hidden_state) and current_index == len(tf_cell_state)

        current_index = 0
        for i, hidden_size in enumerate(config.hidden_layers):
            layer_hidden_state = our_hidden_state[current_index:current_index + hidden_size]
            layer_cell_state = our_cell_state[current_index:current_index + hidden_size]
            our_implementation.hidden[i] = [layer_hidden_state, layer_cell_state]

            current_index += hidden_size

        assert current_index == len(our_hidden_state) and current_index == len(our_cell_state)
    elif brain_configuration["type"] == "GRU" or brain_configuration["type"] == "RNN":
        current_index = 0
        for i, hidden_units in enumerate(config.hidden_layers):
            tf_implementation.hidden[i] = tf.convert_to_tensor(
                tf_hidden_state[current_index:current_index + hidden_units].reshape(1, -1)
            )

            current_index += hidden_units

        assert current_index == len(tf_hidden_state)

        current_index = 0
        for i, hidden_units in enumerate(config.hidden_layers):
            our_implementation.hidden[i] = our_hidden_state[current_index:current_index + hidden_units]

            current_index += hidden_units

        assert current_index == len(our_hidden_state)

    return tf_implementation, our_implementation


class TestTensorflowComparison:

    def test_tensorflow_comparison(self, tensorflow_cmp_configs: List[Dict]):
        for config in tensorflow_cmp_configs:
            tf_impl, our_impl = get_rnn_implementations(config, INPUT_SIZE, OUTPUT_SIZE)

            inputs = np.random.randn(NUMBER_INPUTS, INPUT_SIZE).astype(np.float32)

            tf_lstm_outputs = []
            our_lstm_outputs = []

            new_lstm_times = []
            tf_times = []

            # Go through each input, compute the output of both implementations and compare them in the end
            for i, curr_input in enumerate(inputs):
                time_s_tf = time.time()
                tf_lstm_output = tf_impl.step(curr_input)
                time_e_tf = time.time()
                tf_times.append(time_e_tf - time_s_tf)

                tf_lstm_outputs.append(tf_lstm_output)

                time_s = time.time()
                our_lstm_output = our_impl.step(curr_input)
                time_e = time.time()
                new_lstm_times.append(time_e - time_s)

                our_lstm_outputs.append(our_lstm_output)

                # Set the hidden state to be equal after each computation to avoid build up of numerical errors.
                # Not doing this would result in different computations between the implementations although they might
                # be correct.
                for j, hidden_layer in enumerate(tf_impl.hidden):
                    if config["type"] == "LSTM":
                        our_impl.hidden[j] = [hidden_layer[0].numpy().flatten(), hidden_layer[1].numpy().flatten()]
                    elif config["type"] == "GRU" or config["type"] == "RNN":
                        our_impl.hidden[j] = hidden_layer[0].numpy().flatten()
                    else:
                        raise RuntimeError(f"Unsupported rnn_type '{config['type']}'")

            tf_lstm_outputs = np.array(tf_lstm_outputs)
            our_lstm_outputs = np.array(our_lstm_outputs)

            assert len(tf_lstm_outputs) == len(our_lstm_outputs)
            assert tf_lstm_outputs.size == our_lstm_outputs.size

            assert (np.max(tf_lstm_outputs) <= 1.0
                    and np.max(our_lstm_outputs) <= 1.0
                    and np.min(tf_lstm_outputs) >= -1.0
                    and np.min(our_lstm_outputs) >= -1.0), "Outputs of the brains must be in the [-1, 1] range."

            close_percentage = np.count_nonzero(
               np.isclose(our_lstm_outputs, tf_lstm_outputs, atol=0.00001)) / tf_lstm_outputs.size
            assert close_percentage > 0.90

            print(f"Close predictions between the TensorFlow and NumPy implementations of the {config['type']}: "
                  f"{close_percentage * 100:.2f}% of {tf_lstm_outputs.size} predictions")

            new_lstm_times = np.array(new_lstm_times)
            tf_times = np.array(tf_times)

            print(f"Our {config['type']} times: Mean {np.mean(new_lstm_times)} - Std {np.std(new_lstm_times)} - "
                  f"min {np.min(new_lstm_times)} - max {np.max(new_lstm_times)}")
            print(f"TensorFlow {config['type']} times: Mean {np.mean(tf_times)} - Std {np.std(tf_times)} - "
                  f"min {np.min(tf_times)} - max {np.max(tf_times)}")
            print("---")
