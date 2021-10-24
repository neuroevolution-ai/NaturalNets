import numpy as np
from naturalnets.brains.i_layer_based_brain import ILayerBasedBrain
from naturalnets.brains.i_brain import registered_brain_classes

class GruNN(ILayerBasedBrain):

    @staticmethod
    def get_number_hidden_values():
        return 1

    @staticmethod
    def layer_step(layer_input, weight_ih, weight_hh, bias_h, hidden):
        # Reset Gate
        r_t = ILayerBasedBrain.sigmoid(
            np.dot(weight_ih[0], layer_input)
            + np.dot(weight_hh[0], hidden[0])
            + bias_h[0])

        # Update Gate
        z_t = ILayerBasedBrain.sigmoid(
            np.dot(weight_ih[1], layer_input)
            + np.dot(weight_hh[1], hidden[0])
            + bias_h[1])

        # New Gate
        n_t = np.tanh(
            np.dot(weight_ih[2], layer_input)
            + np.multiply(r_t, np.dot(weight_hh[2], hidden[0]))
            + bias_h[2])

        result = np.multiply(1 - z_t, n_t) + np.multiply(z_t, hidden[0])
        return [[result], result]

    @staticmethod
    def get_number_gates():
        return 3


# TODO: Do this registration via class decorator
registered_brain_classes['GRUNN'] = GruNN
