import numpy as np
from scipy import sparse


class ContinuousTimeRNN:

    def __init__(self, individual, delta_t, number_neurons, v_mask, w_mask, t_mask, clipping_range_min,
                 clipping_range_max):

        self.delta_t = delta_t
        self.number_neurons = number_neurons
        self.clipping_range_min = clipping_range_min
        self.clipping_range_max = clipping_range_max

        # insert weights-values into weight-masks to receive weight-matrices
        # explanation here: https://stackoverflow.com/a/61968524/5132456
        V_size: int = np.count_nonzero(v_mask)
        W_size: int = np.count_nonzero(w_mask)
        T_size: int = np.count_nonzero(t_mask)
        self.V = sparse.csr_matrix(v_mask, dtype=float)
        self.W = sparse.csr_matrix(w_mask, dtype=float)
        self.T = sparse.csr_matrix(t_mask, dtype=float)
        self.V.data[:] = [element for element in individual[0:V_size]]
        self.W.data[:] = [element for element in individual[V_size:V_size + W_size]]
        self.T.data[:] = [element for element in individual[V_size + W_size:V_size + W_size + T_size]]

        # Set x0
        self.reset()

    def step(self, u):

        assert u.ndim == 1

        # Differential equation
        dx_dt = self.W.dot(np.tanh(self.x)) + self.V.dot(u)

        # Euler forward discretization
        self.x = self.x + self.delta_t * dx_dt

        # Clip y to state boundaries
        self.x = np.clip(self.x, self.clipping_range_min, self.clipping_range_max)

        # Calculate outputs
        y = np.tanh(self.T.dot(self.x))

        assert y.ndim == 1

        return y

    def reset(self):
        self.x = np.zeros(self.number_neurons)

    @classmethod
    def generate_masks(cls, number_inputs, number_neurons, number_outputs, v_mask_param, w_mask_param, t_mask_param):

        v_mask = cls._generate_mask(number_neurons, number_inputs, v_mask_param)
        w_mask = cls._generate_mask(number_neurons, number_neurons, w_mask_param)
        t_mask = cls._generate_mask(number_outputs, number_neurons, t_mask_param)

        return v_mask, w_mask, t_mask

    @staticmethod
    def _generate_mask(n, m, mask_param):
        return np.random.rand(n, m) < mask_param

    @staticmethod
    def get_individual_size(v_mask, w_mask, t_mask):

        free_parameters_V = np.count_nonzero(v_mask)
        free_parameters_W = np.count_nonzero(w_mask)
        free_parameters_T = np.count_nonzero(t_mask)

        print("Free parameters: V: {}, W: {}, T: {}".format(free_parameters_V, free_parameters_W, free_parameters_T))

        return free_parameters_V + free_parameters_W + free_parameters_T
