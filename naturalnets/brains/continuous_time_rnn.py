import attrs
import numpy as np

from naturalnets.brains.i_brain import IBrain, IBrainCfg, register_brain_class


@attrs.define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class ContinuousTimeRNNCfg(IBrainCfg):
    delta_t: float
    number_neurons: int
    differential_equation: str
    v_mask: str = 'dense'
    v_mask_density: float = 1.0
    w_mask: str = 'dense'
    w_mask_density: float = 1.0
    t_mask: str = 'dense'
    t_mask_density: float = 1.0
    clipping_range: float = attrs.field(default=1.0, converter=float)
    set_principle_diagonal_elements_of_W_negative: bool = False
    alpha: float = 0.0
    optimize_x0: bool = False


@register_brain_class
class CTRNN(IBrain):

    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: dict,
                 brain_state: dict):

        assert len(individual) == self.get_individual_size(input_size, output_size, configuration, brain_state)

        self.config = ContinuousTimeRNNCfg(**configuration)

        v_mask, w_mask, t_mask = self.get_masks_from_brain_state(brain_state)

        # insert weights-values into weight-masks to receive weight-matrices
        # explanation here: https://stackoverflow.com/a/61968524/5132456
        v_size: int = np.count_nonzero(v_mask)
        w_size: int = np.count_nonzero(w_mask)
        t_size: int = np.count_nonzero(t_mask)

        # Get weight matrizes of current individual
        self.V = np.array([[element] for element in individual[0:v_size]])
        self.W = np.array([[element] for element in individual[v_size:v_size + w_size]])
        self.T = np.array([[element] for element in individual[v_size + w_size:v_size + w_size + t_size]])

        self.V = self.V.reshape([self.config.number_neurons, input_size])
        self.W = self.W.reshape([self.config.number_neurons, self.config.number_neurons])
        self.T = self.T.reshape([output_size, self.config.number_neurons])

        # Set elements of main diagonal to less than 0
        if self.config.set_principle_diagonal_elements_of_W_negative:
            for j in range(self.config.number_neurons):
                self.W[j][j] = -abs(self.W[j][j])

        index = v_size + w_size + t_size

        # Initial state values x0
        if self.config.optimize_x0:
            self.x0 = np.array([element for element in individual[index:index + self.config.number_neurons]])
            index += self.config.number_neurons
        else:
            self.x0 = np.zeros(self.config.number_neurons)

        self.x = self.x0

    def step(self, u):

        assert u.ndim == 1

        # Differential equation
        if self.config.differential_equation == 'NaturalNet':
            dx_dt = -self.config.alpha * self.x + self.W.dot(np.tanh(self.x)) + self.V.dot(u)
        elif self.config.differential_equation == 'LiHoChow2005':
            dx_dt = -self.config.alpha * self.x + self.W.dot(np.tanh(self.x + self.V.dot(u)))
        else:
            raise RuntimeError("No valid differential equation")

        # Euler forward discretization
        self.x = self.x + self.config.delta_t * dx_dt

        # Clip y to state boundaries
        self.x = np.clip(self.x, -self.config.clipping_range, +self.config.clipping_range)

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
        w_mask = cls._generate_mask(config.w_mask, config.number_neurons, config.number_neurons, config.w_mask_density,
                                    True)
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

        free_parameters = {
            'V': free_parameters_v,
            'W': free_parameters_w,
            'T': free_parameters_t
        }

        if configuration["optimize_x0"]:
            free_parameters["x_0"] = configuration["number_neurons"]

        return free_parameters
