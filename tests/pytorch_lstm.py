import abc

import torch
from attr import attr
from gym.spaces import flatdim
from torch import nn
import numpy as np

from brains.i_brain import IBrain, IBrainCfg


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class LstmTorchCfg(IBrainCfg):
    num_layers: int
    hidden_size: int
    use_bias: bool = False


class LSTMPyTorch(nn.Module, IBrain):

    def reset(self):
        self.hidden = (
            torch.randn(self.config.num_layers, 1, self.config.hidden_size),
            torch.randn(self.config.num_layers, 1, self.config.hidden_size)
        )

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: LstmTorchCfg):
        pass

    @classmethod
    def save_brain_state(cls, path, brain_state):
        pass

    def __init__(self, input_size, output_size, individual: np.ndarray, config: LstmTorchCfg, brain_state):
        nn.Module.__init__(self)
        self.config = config
        self.output_size = flatdim(self.output_space)
        input_size = flatdim(self.input_space)
        assert len(individual) == self.get_individual_size(input_size, output_size, config, {})

        if config.num_layers <= 0:
            raise RuntimeError("PyTorch need at least one layer.")

        # Disable tracking of the gradients since backpropagation is not used
        with torch.no_grad():
            self.brain = nn.LSTM(
                input_size=input_size, hidden_size=config.hidden_size,
                num_layers=config.num_layers, bias=config.use_bias)

            # Iterate through all layers and assign the weights from the individual
            current_index = 0
            for i in range(config.num_layers):
                attr_weight_ih_li = "weight_ih_l{}".format(i)
                attr_weight_hh_li = "weight_hh_l{}".format(i)

                weight_ih_li = getattr(self.brain, attr_weight_ih_li)
                weight_hh_li = getattr(self.brain, attr_weight_hh_li)

                weight_ih_li_size = np.prod(weight_ih_li.size())
                weight_hh_li_size = np.prod(weight_hh_li.size())

                # Do not forget to reshape back again
                weight_ih_li.data = torch.from_numpy(
                    individual[current_index: current_index + weight_ih_li_size]).view(weight_ih_li.size()).float()
                current_index += weight_ih_li_size

                weight_hh_li.data = torch.from_numpy(
                    individual[current_index: current_index + weight_hh_li_size]).view(weight_hh_li.size()).float()
                current_index += weight_hh_li_size

                if config.use_bias:
                    attr_bias_ih_li = "bias_ih_l{}".format(i)
                    attr_bias_hh_li = "bias_hh_l{}".format(i)

                    bias_ih_li = getattr(self.brain, attr_bias_ih_li)
                    bias_hh_li = getattr(self.brain, attr_bias_hh_li)

                    bias_ih_li_size = bias_ih_li.size()[0]
                    bias_hh_li_size = bias_hh_li.size()[0]

                    bias_ih_li.data = torch.from_numpy(
                        individual[current_index: current_index + bias_ih_li_size]).float()
                    current_index += bias_ih_li_size

                    bias_hh_li.data = torch.from_numpy(
                        individual[current_index: current_index + bias_hh_li_size]).float()
                    current_index += bias_hh_li_size
            self.weight_ho = np.array(
                individual[current_index: current_index + self.output_size * config.hidden_size]).reshape(
                (self.output_size, config.hidden_size))
            current_index += self.output_size * config.hidden_size
            assert current_index == len(individual)

            self.hidden = (
                torch.randn(config.num_layers, 1, config.hidden_size),
                torch.randn(config.num_layers, 1, config.hidden_size)
            )

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, config: LstmTorchCfg, brain_state):
        num_layers = config.num_layers
        number_gates = 4
        hidden_size = config.hidden_size
        index = 0
        # size of the learnable input-hidden weights

        index += hidden_size * input_size * number_gates
        if num_layers > 1:
            index += hidden_size * hidden_size * (num_layers - 1) * number_gates

        # size of the learnable hidden-hidden weights
        index += hidden_size * hidden_size * num_layers * number_gates

        if config.use_bias:
            index += 2 * hidden_size * num_layers * number_gates
        index += output_size * hidden_size
        return {"all": index}

    def step(self, ob: np.ndarray):

        with torch.no_grad():
            # Input requires the form (seq_len, batch, input_size)
            out, self.hidden = self.brain(torch.from_numpy(ob.astype(np.float32)).view(1, 1, -1), self.hidden)
            return np.dot(self.weight_ho, out.flatten())
