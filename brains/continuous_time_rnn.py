import attr
import numpy as np
from scipy import sparse
from brains.i_brain import IBrain, IBrainCfg, registered_brain_classes


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class ContinuousTimeRNNCfg(IBrainCfg):
    delta_t: float
    number_neurons: int
    v_mask: str = 'dense'
    v_mask_density: float = 1.0
    w_mask: str = 'dense'
    w_mask_density: float = 1.0
    t_mask: str = 'dense'
    t_mask_density: float = 1.0
    clipping_range_min: float = 1.0
    clipping_range_max: float = -1.0


class ContinuousTimeRNN(IBrain):

    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: dict,
                 brain_state: dict):

        self.config = ContinuousTimeRNNCfg(**configuration)

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
        self.x = np.zeros(self.config.number_neurons)

    def step(self, u):

        assert u.ndim == 1

        # Differential equation
        dx_dt = self.W.dot(np.tanh(self.x)) + self.V.dot(u)

        # Euler forward discretization
        self.x = self.x + self.config.delta_t * dx_dt

        # Clip y to state boundaries
        self.x = np.clip(self.x, self.config.clipping_range_min, self.config.clipping_range_max)

        # Calculate outputs
        y = np.tanh(self.T.dot(self.x))

        assert y.ndim == 1

        return y

    def reset(self):
        self.x = np.zeros(self.config.number_neurons)

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: dict):

        config = ContinuousTimeRNNCfg(**configuration)

        v_mask = cls._generate_mask(config.v_mask, config.number_neurons, input_size, config.v_mask_density)
        w_mask = cls._generate_mask(config.w_mask, config.number_neurons, config.number_neurons, config.w_mask_density, True)
        t_mask = cls._generate_mask(config.t_mask, output_size, config.number_neurons, config.t_mask_density)

        return cls.get_brain_state_from_masks(v_mask, w_mask, t_mask)

    @staticmethod
    def _generate_mask(mask_type, n, m, mask_density, keep_main_diagonal=False):

        if mask_type == "random":
            mask = np.random.rand(n, m) < mask_density
        elif mask_type == "dense":
            mask = np.ones((n, m), dtype=bool)
        else:
            raise RuntimeError("Unknown mask_type: " + str(mask_type))

        if keep_main_diagonal:
            assert n == m
            for i in range(n):
                mask[i, i] = True

        return mask

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
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):

        v_mask, w_mask, t_mask = cls.get_masks_from_brain_state(brain_state)

        free_parameters_v = np.count_nonzero(v_mask)
        free_parameters_w = np.count_nonzero(w_mask)
        free_parameters_t = np.count_nonzero(t_mask)

        return {'V': free_parameters_v, 'W': free_parameters_w, 'T': + free_parameters_t}


# TODO: Do this registration via class decorator
registered_brain_classes['CTRNN'] = ContinuousTimeRNN
