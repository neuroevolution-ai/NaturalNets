import time

import numpy as np
import torch

from naturalnets.brains import LstmNN, GruNN, ElmanNN
from naturalnets.brains.i_layer_based_brain import ILayerBasedBrainCfg
from tests.pytorch_brains import IPytorchBrainCfg, GruPyTorch, LstmPyTorch, ElmanPyTorch


class TestPyTorch:

    def test_gru_output(self, numpy_config: ILayerBasedBrainCfg, torch_config: IPytorchBrainCfg):
        input_size = 28
        output_size = 8

        number_of_inputs = 10000

        individual_size = GruPyTorch.get_individual_size(input_size, output_size, torch_config, {})

        # Make two copies to avoid possible errors due to PyTorch reusing data from the same memory address
        individual_pytorch = np.random.randn(individual_size).astype(np.float32)
        individual_numpy = np.copy(individual_pytorch)

        with torch.no_grad():
            gru_pytorch = GruPyTorch(input_size, output_size, individual_pytorch, torch_config, {})

        gru_numpy = GruNN(input_size, output_size, individual_numpy, numpy_config, {})

        # Also initialize the values for the hidden and cell states the same
        hidden_pytorch = np.random.randn(*gru_pytorch.hidden.size()).astype(np.float32)

        hidden_numpy = np.copy(hidden_pytorch).reshape(len(numpy_config.hidden_layer_structure), -1)

        gru_pytorch.hidden = torch.from_numpy(hidden_pytorch)

        gru_numpy.hidden = [[np.copy(hidden_numpy)[i]] for i in
                            range(len(np.copy(hidden_numpy)))]
        with torch.no_grad():
            for i in range(len(numpy_config.hidden_layer_structure)):
                attr_weight_ih_li = "weight_ih_l{}".format(i)
                attr_weight_hh_li = "weight_hh_l{}".format(i)
                weight_ih = "weight_ih".format(i)
                weight_hh = "weight_hh".format(i)

                weight_ih_li_pytorch = getattr(gru_pytorch.brain, attr_weight_ih_li).detach().numpy()
                weight_hh_li_pytorch = getattr(gru_pytorch.brain, attr_weight_hh_li).detach().numpy()

                weight_ih_li_numpy = getattr(gru_numpy, weight_ih)[i].reshape(weight_ih_li_pytorch.shape)
                weight_hh_li_numpy = getattr(gru_numpy, weight_hh)[i].reshape(weight_hh_li_pytorch.shape)

                assert np.array_equal(weight_ih_li_pytorch, weight_ih_li_numpy)
                assert np.array_equal(weight_hh_li_pytorch, weight_hh_li_numpy)

                # Check hidden states
                assert np.array_equal(gru_pytorch.hidden[i].view(-1).detach().numpy(), gru_numpy.hidden[i][0])

            # Check output matrix
            assert np.array_equal(gru_pytorch.weight_ho, gru_numpy.weight_ho)

        self.compare_outputs(number_of_inputs=number_of_inputs, input_size=input_size, pytorch_network=gru_pytorch,
                             numpy_network=gru_numpy)

    def test_elman_output(self, numpy_config: ILayerBasedBrainCfg, torch_config: IPytorchBrainCfg):
        input_size = 28
        output_size = 8

        number_of_inputs = 10000

        individual_size = ElmanPyTorch.get_individual_size(input_size, output_size, torch_config, {})

        # Make two copies to avoid possible errors due to PyTorch reusing data from the same memory address
        individual_pytorch = np.random.randn(individual_size).astype(np.float32)
        individual_numpy = np.copy(individual_pytorch)

        with torch.no_grad():
            elman_pytorch = ElmanPyTorch(input_size, output_size, individual_pytorch, torch_config, {})

        elman_numpy = ElmanNN(input_size, output_size, individual_numpy, numpy_config, {})

        # Also initialize the values for the hidden and cell states the same
        hidden_pytorch = np.random.randn(*elman_pytorch.hidden.size()).astype(np.float32)

        hidden_numpy = np.copy(hidden_pytorch).reshape(len(numpy_config.hidden_layer_structure), -1)

        elman_pytorch.hidden = torch.from_numpy(hidden_pytorch)

        elman_numpy.hidden = [[np.copy(hidden_numpy)[i]] for i in
                            range(len(np.copy(hidden_numpy)))]
        with torch.no_grad():
            for i in range(len(numpy_config.hidden_layer_structure)):
                attr_weight_ih_li = "weight_ih_l{}".format(i)
                attr_weight_hh_li = "weight_hh_l{}".format(i)
                weight_ih = "weight_ih".format(i)
                weight_hh = "weight_hh".format(i)

                weight_ih_li_pytorch = getattr(elman_pytorch.brain, attr_weight_ih_li).detach().numpy()
                weight_hh_li_pytorch = getattr(elman_pytorch.brain, attr_weight_hh_li).detach().numpy()

                weight_ih_li_numpy = getattr(elman_numpy, weight_ih)[i].reshape(weight_ih_li_pytorch.shape)
                weight_hh_li_numpy = getattr(elman_numpy, weight_hh)[i].reshape(weight_hh_li_pytorch.shape)

                assert np.array_equal(weight_ih_li_pytorch, weight_ih_li_numpy)
                assert np.array_equal(weight_hh_li_pytorch, weight_hh_li_numpy)

                # Check hidden states
                assert np.array_equal(elman_pytorch.hidden[i].view(-1).detach().numpy(), elman_numpy.hidden[i][0])

            # Check output matrix
            assert np.array_equal(elman_pytorch.weight_ho, elman_numpy.weight_ho)

        self.compare_outputs(number_of_inputs=number_of_inputs, input_size=input_size, pytorch_network=elman_pytorch,
                             numpy_network=elman_numpy)

    def test_lstm_output(self, numpy_config: ILayerBasedBrainCfg, torch_config: IPytorchBrainCfg):
        input_size = 28
        output_size = 8

        number_of_inputs = 10000

        individual_size = LstmPyTorch.get_individual_size(input_size, output_size, torch_config, {})

        # Make two copies to avoid possible errors due to PyTorch reusing data from the same memory address
        individual_pytorch = np.random.randn(individual_size).astype(np.float32)
        individual_numpy = np.copy(individual_pytorch)

        with torch.no_grad():
            lstm_pytorch = LstmPyTorch(input_size, output_size, individual_pytorch, torch_config, {})

        lstm_numpy = LstmNN(input_size, output_size, individual_numpy, numpy_config, {})

        # Also initialize the values for the hidden and cell states the same
        hidden_pytorch = np.random.randn(*lstm_pytorch.hidden[0].size()).astype(np.float32)
        cell_pytorch = np.random.randn(*lstm_pytorch.hidden[1].size()).astype(np.float32)

        hidden_numpy = np.copy(hidden_pytorch).reshape(len(numpy_config.hidden_layer_structure), -1)
        cell_numpy = np.copy(cell_pytorch).reshape(len(numpy_config.hidden_layer_structure), -1)

        lstm_pytorch.hidden = (torch.from_numpy(hidden_pytorch), torch.from_numpy(cell_pytorch))

        lstm_numpy.hidden = [[np.copy(hidden_numpy)[i], np.copy(cell_numpy)[i]] for i in
                             range(len(np.copy(hidden_numpy)))]

        with torch.no_grad():
            for i in range(len(numpy_config.hidden_layer_structure)):
                attr_weight_ih_li = "weight_ih_l{}".format(i)
                attr_weight_hh_li = "weight_hh_l{}".format(i)
                weight_ih = "weight_ih".format(i)
                weight_hh = "weight_hh".format(i)

                weight_ih_li_pytorch = getattr(lstm_pytorch.brain, attr_weight_ih_li).detach().numpy()
                weight_hh_li_pytorch = getattr(lstm_pytorch.brain, attr_weight_hh_li).detach().numpy()

                weight_ih_li_numpy = getattr(lstm_numpy, weight_ih)[i].reshape(weight_ih_li_pytorch.shape)
                weight_hh_li_numpy = getattr(lstm_numpy, weight_hh)[i].reshape(weight_hh_li_pytorch.shape)

                assert np.array_equal(weight_ih_li_pytorch, weight_ih_li_numpy)
                assert np.array_equal(weight_hh_li_pytorch, weight_hh_li_numpy)

                # Check hidden and cell states
                assert np.array_equal(lstm_pytorch.hidden[0][i].view(-1).detach().numpy(), lstm_numpy.hidden[i][0])
                assert np.array_equal(lstm_pytorch.hidden[1][i].view(-1).detach().numpy(), lstm_numpy.hidden[i][1])

            # Check output matrix
            assert np.array_equal(lstm_pytorch.weight_ho, lstm_numpy.weight_ho)

        self.compare_outputs(number_of_inputs=number_of_inputs, input_size=input_size, pytorch_network=lstm_pytorch,
                             numpy_network=lstm_numpy)

    @staticmethod
    def compare_outputs(number_of_inputs, input_size, pytorch_network, numpy_network):

        inputs = np.random.randn(number_of_inputs, input_size).astype(np.float32)
        lstm_pytorch_outputs = []
        lstm_numpy_outputs = []

        lstm_pytorch_times = []
        lstm_numpy_times = []

        # Collect predictions of PyTorch and NumPy implementations and collect time data
        for i in inputs:
            with torch.no_grad():
                time_s = time.time()
                lstm_pytorch_output = pytorch_network.step(i)
                lstm_pytorch_times.append(time.time() - time_s)
                lstm_pytorch_outputs.append(lstm_pytorch_output)

            time_s = time.time()
            lstm_numpy_output = numpy_network.step(i)
            lstm_numpy_times.append(time.time() - time_s)
            lstm_numpy_outputs.append(lstm_numpy_output)

        lstm_pytorch_outputs = np.array(lstm_pytorch_outputs)
        lstm_numpy_outputs = np.array(lstm_numpy_outputs)

        lstm_pytorch_times = np.array(lstm_pytorch_times)
        lstm_numpy_times = np.array(lstm_numpy_times)

        assert len(lstm_pytorch_outputs) == len(lstm_numpy_outputs)
        assert lstm_pytorch_outputs.size == lstm_numpy_outputs.size

        print("PyTorch Mean Prediction Time {}s | NumPy Mean Prediction Time {}s"
              .format(np.mean(lstm_pytorch_times), np.mean(lstm_numpy_times)))

        print("PyTorch Stddev Prediction Time {}s | NumPy Stddev Prediction Time {}s"
              .format(np.std(lstm_pytorch_times), np.std(lstm_numpy_times)))

        print("PyTorch Max Prediction Time {}s | NumPy Max Prediction Time {}s"
              .format(np.max(lstm_pytorch_times), np.max(lstm_numpy_times)))

        print("PyTorch Min Prediction Time {}s | NumPy Min Prediction Time {}s"
              .format(np.min(lstm_pytorch_times), np.min(lstm_numpy_times)))

        # Use percentage instead of np.allclose() because some results exceed the rtol value, but it is a low percentage
        close_percentage = np.count_nonzero(
            np.isclose(lstm_pytorch_outputs, lstm_numpy_outputs)) / lstm_pytorch_outputs.size
        assert close_percentage > 0.90

        print(
            "Equal predictions between PyTorch and NumPy",
            "Implementation of LSTM: {}% of {} predictions".format(close_percentage * 100, number_of_inputs))
