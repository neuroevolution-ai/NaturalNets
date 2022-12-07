from typing import Dict, Tuple

import numpy as np
from attrs import define, field, validators

from naturalnets.brains.i_brain import IBrain, IBrainCfg, register_brain_class

DENSE_MASK = "dense"
RANDOM_MASK = "random"

NATURAL_NET_DIFF_EQ = "NaturalNet"
LI_HO_CHOW_DIFF_EQ = "LiHoChow2005"


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class ContinuousTimeRNNCfg(IBrainCfg):
    # TODO should delta_t be gt 0, or ge 0, or sth else?
    delta_t: float = field(validator=validators.instance_of(float))
    number_neurons: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    differential_equation: str = field(
        validator=[validators.instance_of(str), validators.in_([NATURAL_NET_DIFF_EQ, LI_HO_CHOW_DIFF_EQ])]
    )
    v_mask: str = field(
        default=DENSE_MASK,
        validator=[validators.instance_of(str), validators.in_([DENSE_MASK, RANDOM_MASK])]
    )
    # TODO can this be negative?
    v_mask_density: float = field(default=1.0, validator=validators.instance_of(float))
    w_mask: str = field(
        default=DENSE_MASK,
        validator=[validators.instance_of(str), validators.in_([DENSE_MASK, RANDOM_MASK])]
    )
    w_mask_density: float = field(default=1.0, validator=validators.instance_of(float))
    t_mask: str = field(
        default=DENSE_MASK,
        validator=[validators.instance_of(str), validators.in_([DENSE_MASK, RANDOM_MASK])]
    )
    t_mask_density: float = field(default=1.0, validator=validators.instance_of(float))
    clipping_range: float = field(default=1.0, converter=float, validator=validators.gt(0))
    set_principle_diagonal_elements_of_W_negative: bool = field(default=False, validator=validators.instance_of(bool))
    # TODO can this be negative (probably not)?
    alpha: float = field(default=0.0, converter=float, validator=validators.instance_of(float))
    optimize_x0: bool = field(default=False, validator=validators.instance_of(bool))


@register_brain_class
class CTRNN(IBrain):

    def __init__(self, input_size: int, output_size: int, individual: np.ndarray, configuration: dict,
                 brain_state: dict):
        super().__init__(input_size, output_size, individual, configuration, brain_state)

        self.config = ContinuousTimeRNNCfg(**configuration)

        v_mask, w_mask, t_mask = self.get_masks_from_brain_state(brain_state)

        # Insert weights-values into weight-masks to receive weight-matrices
        # explanation here: https://stackoverflow.com/a/61968524/5132456
        v_size: int = np.count_nonzero(v_mask)
        w_size: int = np.count_nonzero(w_mask)
        t_size: int = np.count_nonzero(t_mask)

        # Get weight matrices of current individual
        self.V = np.array([[element] for element in individual[0:v_size]])
        self.W = np.array([[element] for element in individual[v_size:v_size + w_size]])
        self.T = np.array([[element] for element in individual[v_size + w_size:v_size + w_size + t_size]])

        self.V = self.V.reshape([self.config.number_neurons, self.input_size])
        self.W = self.W.reshape([self.config.number_neurons, self.config.number_neurons])
        self.T = self.T.reshape([self.output_size, self.config.number_neurons])

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

    def step(self, u: np.ndarray) -> np.ndarray:

        assert u.ndim == 1

        # Differential equation
        if self.config.differential_equation == NATURAL_NET_DIFF_EQ:
            dx_dt = -self.config.alpha * self.x + self.W.dot(np.tanh(self.x)) + self.V.dot(u)
        elif self.config.differential_equation == LI_HO_CHOW_DIFF_EQ:
            dx_dt = -self.config.alpha * self.x + self.W.dot(np.tanh(self.x + self.V.dot(u)))
        else:
            raise RuntimeError(f"'{self.config.differential_equation}' is no valid differential equation")

        # Euler forward discretization
        self.x = self.x + self.config.delta_t * dx_dt

        # Clip y to state boundaries
        self.x = np.clip(self.x, -self.config.clipping_range, +self.config.clipping_range)

        # Calculate outputs
        y = np.tanh(self.T.dot(self.x))

        assert y.ndim == 1

        return y

    def reset(self):
        # TODO fix this when using optimize_x0
        if self.config.optimize_x0:
            raise RuntimeError("CTRNN optimize_x0 is bugged, resetting the brain should take the trained x0, which is"
                               "currently not implemented")

        self.x = np.zeros(self.config.number_neurons)

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: dict) -> Dict[str, np.ndarray]:

        config = ContinuousTimeRNNCfg(**configuration)

        v_mask = cls._generate_mask(config.v_mask, config.number_neurons, input_size, config.v_mask_density)
        w_mask = cls._generate_mask(config.w_mask, config.number_neurons, config.number_neurons, config.w_mask_density,
                                    True)
        t_mask = cls._generate_mask(config.t_mask, output_size, config.number_neurons, config.t_mask_density)

        return cls.get_brain_state_from_masks(v_mask, w_mask, t_mask)

    @staticmethod
    def _generate_mask(mask_type, n, m, mask_density, keep_main_diagonal=False):

        if mask_type == RANDOM_MASK:
            mask = np.random.rand(n, m) < mask_density
        elif mask_type == DENSE_MASK:
            mask = np.ones((n, m), dtype=bool)
        else:
            raise RuntimeError(f"Unknown mask_type: {mask_type}")

        if keep_main_diagonal:
            assert n == m
            for i in range(n):
                mask[i, i] = True

        return mask

    @classmethod
    def register_brain_state_for_saving(cls, model_contents: dict, brain_state: Dict[str, np.ndarray]) -> dict:
        v_mask, w_mask, t_mask = cls.get_masks_from_brain_state(brain_state)

        model_contents["brain_state_v_mask"] = v_mask
        model_contents["brain_state_w_mask"] = w_mask
        model_contents["brain_state_t_mask"] = t_mask

        return model_contents

    @classmethod
    def load_brain_state(cls, brain_data) -> Dict[str, np.ndarray]:
        v_mask = brain_data["brain_state_v_mask"]
        w_mask = brain_data["brain_state_w_mask"]
        t_mask = brain_data["brain_state_t_mask"]

        return cls.get_brain_state_from_masks(v_mask, w_mask, t_mask)

    @staticmethod
    def get_masks_from_brain_state(brain_state: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:

        v_mask = brain_state["v_mask"]
        w_mask = brain_state["w_mask"]
        t_mask = brain_state["t_mask"]

        return v_mask, w_mask, t_mask

    @staticmethod
    def get_brain_state_from_masks(v_mask: np.ndarray, w_mask: np.ndarray, t_mask: np.ndarray) -> Dict[str, np.ndarray]:
        return {"v_mask": v_mask, "w_mask": w_mask, "t_mask": t_mask}

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):

        v_mask, w_mask, t_mask = cls.get_masks_from_brain_state(brain_state)

        free_parameters_v = np.count_nonzero(v_mask)
        free_parameters_w = np.count_nonzero(w_mask)
        free_parameters_t = np.count_nonzero(t_mask)

        free_parameters = {
            "V": free_parameters_v,
            "W": free_parameters_w,
            "T": free_parameters_t
        }

        if configuration["optimize_x0"]:
            free_parameters["x_0"] = configuration["number_neurons"]

        number_of_output_neurons_start_index = free_parameters_v + free_parameters_w
        number_of_output_neurons_end_index = number_of_output_neurons_start_index + free_parameters_t

        return free_parameters, number_of_output_neurons_start_index, number_of_output_neurons_end_index
