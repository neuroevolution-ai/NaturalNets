import abc
import attr
import numpy as np
import torch
from torch import nn

from naturalnets.brains.i_brain import IBrain, IBrainCfg


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class IPytorchBrainCfg(IBrainCfg):
    num_layers: int
    hidden_size: int
    use_bias: bool = False


class IPytorchBrain(nn.Module, IBrain, abc.ABC):

    def __init__(self, input_size, output_size, individual: np.ndarray, config: IPytorchBrainCfg, brain_state):
        nn.Module.__init__(self)
        assert len(individual) == self.get_individual_size(
            input_size=input_size, output_size=output_size, configuration=config, brain_state=brain_state)
        self.config = config
        if config.num_layers <= 0:
            raise RuntimeError("PyTorch need at least one layer.")

        # Disable tracking of the gradients since backpropagation is not used
        with torch.no_grad():
            self.brain = self.get_brain(config, input_size)

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
                individual[current_index: current_index + output_size * config.hidden_size]).reshape(
                (output_size, config.hidden_size))
            current_index += output_size * config.hidden_size
            assert current_index == len(individual)

            self.hidden = self.get_hidden(config)

    def reset(self):
        self.hidden = self.get_hidden(self.config)

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: IPytorchBrainCfg):
        pass

    @classmethod
    def save_brain_state(cls, path, brain_state):
        pass

    @classmethod
    def get_free_parameter_usage(cls, input_size, output_size, config: IPytorchBrainCfg, brain_state):
        num_layers = config.num_layers
        number_gates = cls.get_number_gates()
        hidden_size = config.hidden_size
        # size of the learnable input-hidden weights
        individuals = {
            'input_weight_matrix': hidden_size * input_size * number_gates + (
                hidden_size * hidden_size * (num_layers - 1) * number_gates if num_layers > 1 else 0),
            'hidden_weight_matrix': hidden_size * hidden_size * num_layers * number_gates,
            'output_weight_matrix': output_size * hidden_size
        }
        if config.use_bias:
            individuals['bias'] = 2 * hidden_size * num_layers * number_gates
        return individuals

    @staticmethod
    @abc.abstractmethod
    def get_number_gates():
        pass

    @abc.abstractmethod
    def get_brain(self, config: IPytorchBrainCfg, input_size):
        pass

    @staticmethod
    @abc.abstractmethod
    def get_hidden(config: IPytorchBrainCfg):
        pass

    def step(self, ob: np.ndarray):
        with torch.no_grad():
            # Input requires the form (seq_len, batch, input_size)
            out, self.hidden = self.brain(torch.from_numpy(ob.astype(np.float32)).view(1, 1, -1), self.hidden)
            return np.tanh(np.dot(self.weight_ho, out.flatten()))


class LstmPyTorch(IPytorchBrain):

    def __init__(self, input_size, output_size, individual: np.ndarray, config: IPytorchBrainCfg, brain_state):
        IPytorchBrain.__init__(self, input_size, output_size, individual, config, brain_state)

    def get_brain(self, config: IPytorchBrainCfg, input_size):
        return nn.LSTM(
            input_size=input_size, hidden_size=config.hidden_size,
            num_layers=config.num_layers, bias=config.use_bias)

    @staticmethod
    def get_hidden(config: IPytorchBrainCfg):
        return (
            torch.randn(config.num_layers, 1, config.hidden_size),
            torch.randn(config.num_layers, 1, config.hidden_size)
        )

    @staticmethod
    def get_number_gates():
        return 4


class GruPyTorch(IPytorchBrain):

    def __init__(self, input_size, output_size, individual: np.ndarray, config: IPytorchBrainCfg, brain_state):
        IPytorchBrain.__init__(self, input_size, output_size, individual, config, brain_state)

    def get_brain(self, config: IPytorchBrainCfg, input_size):
        return nn.GRU(
            input_size=input_size, hidden_size=config.hidden_size,
            num_layers=config.num_layers, bias=config.use_bias)

    @staticmethod
    def get_hidden(config: IPytorchBrainCfg):
        return (
            torch.randn(config.num_layers, 1, config.hidden_size)
        )

    @staticmethod
    def get_number_gates():
        return 3


class ElmanPyTorch(IPytorchBrain):

    def __init__(self, input_size, output_size, individual: np.ndarray, config: IPytorchBrainCfg, brain_state):
        IPytorchBrain.__init__(self, input_size, output_size, individual, config, brain_state)

    def get_brain(self, config: IPytorchBrainCfg, input_size):
        return nn.RNN(
            input_size=input_size, hidden_size=config.hidden_size,
            num_layers=config.num_layers, bias=config.use_bias)

    @staticmethod
    def get_hidden(config: IPytorchBrainCfg):
        return (
            torch.zeros(config.num_layers, 1, config.hidden_size)
        )

    @staticmethod
    def get_number_gates():
        return 1
