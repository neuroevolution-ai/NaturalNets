import numpy as np
from scipy import sparse


class ContinuousTimeRNN:

    def __init__(self, individual, delta_t, number_neurons, brain_state, clipping_range_min,
                 clipping_range_max):

        self.delta_t = delta_t
        self.number_neurons = number_neurons
        self.clipping_range_min = clipping_range_min
        self.clipping_range_max = clipping_range_max

        v_mask, w_mask, t_mask = self.get_masks_from_brain_state(brain_state)

        # insert weights-values into weight-masks to receive weight-matrices
        # explanation here: https://stackoverflow.com/a/61968524/5132456
        v_size: int = np.count_nonzero(v_mask)
        w_size: int = np.count_nonzero(w_mask)
        t_size: int = np.count_nonzero(t_mask)

        self.V = sparse.csr_matrix(v_mask, dtype=float)
        self.W = sparse.csr_matrix(w_mask, dtype=float)
        self.T = sparse.csr_matrix(t_mask, dtype=float)

        self.V.data[:] = [element for element in individual[0:v_size]]
        self.W.data[:] = [element for element in individual[v_size:v_size + w_size]]
        self.T.data[:] = [element for element in individual[v_size + w_size:v_size + w_size + t_size]]

        # Set x0
        self.x = np.zeros(self.number_neurons)

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
    def generate_brain_state(cls, number_inputs, number_neurons, number_outputs, v_mask_param, w_mask_param,
                             t_mask_param):

        v_mask = cls._generate_mask(number_neurons, number_inputs, v_mask_param)
        w_mask = cls._generate_mask(number_neurons, number_neurons, w_mask_param)
        t_mask = cls._generate_mask(number_outputs, number_neurons, t_mask_param)

        return cls.get_brain_state_from_masks(v_mask, w_mask, t_mask)

    @staticmethod
    def _generate_mask(n, m, mask_param):
        return np.random.rand(n, m) < mask_param

    @classmethod
    def save_brain_state(cls, path, brain_state):
        v_mask, w_mask, t_mask = cls.get_masks_from_brain_state(brain_state)

        np.savez(path, v_mask=v_mask, w_mask=w_mask, t_mask=t_mask)

    @classmethod
    def load_brain_state(cls, path):

        file_data = np.load(path)

        v_mask = file_data['v_mask']
        w_mask = file_data['w_mask']
        t_mask = file_data['t_mask']

        return cls.get_brain_state_from_masks(v_mask, w_mask, t_mask)

    @staticmethod
    def get_masks_from_brain_state(brain_state):

        v_mask = brain_state['v_mask']
        w_mask = brain_state['w_mask']
        t_mask = brain_state['t_mask']

        return v_mask, w_mask, t_mask

    @staticmethod
    def get_brain_state_from_masks(v_mask, w_mask, t_mask):
        return {"v_mask": v_mask, "w_mask": w_mask, "t_mask": t_mask}

    @classmethod
    def get_individual_size(cls, brain_state):

        v_mask, w_mask, t_mask = cls.get_masks_from_brain_state(brain_state)

        free_parameters_v = np.count_nonzero(v_mask)
        free_parameters_w = np.count_nonzero(w_mask)
        free_parameters_t = np.count_nonzero(t_mask)

        print("Free parameters: V: {}, W: {}, T: {}".format(free_parameters_v, free_parameters_w, free_parameters_t))

        return free_parameters_v + free_parameters_w + free_parameters_t
