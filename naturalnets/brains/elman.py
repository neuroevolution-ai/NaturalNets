import numpy as np

from naturalnets.brains.i_brain import register_brain_class
from naturalnets.brains.i_layer_based_brain import ILayerBasedBrain


@register_brain_class
class ElmanNN(ILayerBasedBrain):

    @staticmethod
    def get_number_hidden_values():
        return 1

    @staticmethod
    def get_number_gates():
        return 1

    @staticmethod
    def layer_step(layer_input: np.ndarray, weight_ih, weight_hh, bias_h, hidden):
        result = np.tanh(
            np.dot(weight_ih[0], layer_input)
            + np.dot(weight_hh[0], hidden[0])
            + bias_h[0]
        )
        return [[result], result]
