import numpy as np

from naturalnets.brains.i_brain import register_brain_class
from naturalnets.brains.i_layer_based_brain import ILayerBasedBrain


@register_brain_class
class LSTM(ILayerBasedBrain):

    @staticmethod
    def get_number_hidden_values():
        return 2

    @staticmethod
    def get_number_gates():
        return 4

    @staticmethod
    def layer_step(layer_input: np.ndarray, weight_ih, weight_hh, bias_h, hidden):
        # Input Gate
        i_t = ILayerBasedBrain.sigmoid(np.dot(weight_ih[0], layer_input)
                                       + bias_h[0]
                                       + np.dot(weight_hh[0], hidden[0]))
        # Forget Gate
        f_t = ILayerBasedBrain.sigmoid(np.dot(weight_ih[1], layer_input)
                                       + bias_h[1]
                                       + np.dot(weight_hh[1], hidden[0]))
        # Cell Gate
        g_t = np.tanh(np.dot(weight_ih[2], layer_input)
                      + bias_h[2]
                      + np.dot(weight_hh[2], hidden[0]))
        # Output Gate
        o_t = ILayerBasedBrain.sigmoid(np.dot(weight_ih[3], layer_input)
                                       + bias_h[3]
                                       + np.dot(weight_hh[3], hidden[0]))

        cell_state = np.multiply(f_t, hidden[1]) + np.multiply(i_t, g_t)
        hid = np.multiply(o_t, np.tanh(cell_state))

        return [[hid, cell_state], hid]
