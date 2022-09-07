from typing import Dict

import numpy as np
import tensorflow as tf

from naturalnets.brains import LSTM
from naturalnets.brains.i_layer_based_brain import ILayerBasedBrainCfg
from tests.brains.tensorflow_brains import TensorflowLSTM


def get_lstm_implementations(brain_configuration, input_size, output_size):
    individual_size = LSTM.get_individual_size(input_size, output_size, brain_configuration, {})

    config = ILayerBasedBrainCfg(**brain_configuration)

    # Make two copies to avoid possible errors due to PyTorch reusing data from the same memory address
    individual_tensorflow = np.random.randn(individual_size).astype(np.float32)
    individual_ours = np.copy(individual_tensorflow)

    tf_lstm = TensorflowLSTM(input_size, output_size, individual=individual_tensorflow, configuration=config,
                             brain_state={})

    our_lstm = LSTM(input_size, output_size, individual=individual_ours, configuration=config, brain_state={})

    tf_hidden_state = np.random.randn(np.sum(config.hidden_layer_structure)).astype(np.float32)
    tf_cell_state = np.random.randn(np.sum(config.hidden_layer_structure)).astype(np.float32)

    our_hidden_state = np.copy(tf_hidden_state)
    our_cell_state = np.copy(tf_cell_state)

    current_index = 0
    for i, layer in enumerate(tf_lstm.lstm_layers):
        num_units = layer.units
        tf_lstm.hidden[i] = [
            tf.convert_to_tensor(tf_hidden_state[current_index:current_index + num_units].reshape((1, num_units))),
            tf.convert_to_tensor(tf_cell_state[current_index:current_index + num_units].reshape((1, num_units)))
        ]

        current_index += num_units

    assert current_index == len(tf_hidden_state) and current_index == len(tf_cell_state)

    current_index = 0
    for i, hidden_size in enumerate(config.hidden_layer_structure):
        layer_hidden_state = our_hidden_state[current_index:current_index + hidden_size]
        layer_cell_state = our_cell_state[current_index:current_index + hidden_size]
        our_lstm.hidden[i] = np.concatenate((layer_hidden_state, layer_cell_state)).reshape((-1, hidden_size))

        current_index += hidden_size

    assert current_index == len(our_hidden_state) and current_index == len(our_cell_state)

    return tf_lstm, our_lstm


class TestTensorflowComparison:

    def test_lstm_output(self, brain_config: Dict):
        input_size = 28
        output_size = 8

        number_of_inputs = 1000

        tf_lstm, our_lstm = get_lstm_implementations(brain_config, input_size, output_size)

        inputs = np.random.randn(number_of_inputs, input_size).astype(np.float32)

        tf_lstm_outputs = []
        our_lstm_outputs = []

        for i in inputs:
            tf_lstm_output = tf_lstm.step(i)
            tf_lstm_outputs.append(tf_lstm_output)

            our_lstm_output = our_lstm.step(i)
            our_lstm_outputs.append(our_lstm_output)

        tf_lstm_outputs = np.array(tf_lstm_outputs)
        our_lstm_outputs = np.array(our_lstm_outputs)

        assert len(tf_lstm_outputs) == len(our_lstm_outputs)
        assert tf_lstm_outputs.size == our_lstm_outputs.size

        close_percentage = np.count_nonzero(np.isclose(tf_lstm_outputs, our_lstm_outputs)) / tf_lstm_outputs.size
        assert close_percentage > 0.90

        print("Close predictions between the TensorFlow and NumPy implementations of the LSTM: "
              f"{close_percentage * 100:.2f}% of {tf_lstm_outputs.size} predictions")


