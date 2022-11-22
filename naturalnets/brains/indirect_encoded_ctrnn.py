from typing import Union, Dict, Optional

import attr
import numpy as np

from naturalnets.brains.continuous_time_rnn import CTRNN
from naturalnets.brains.feed_forward_nn import FeedForwardNN
from naturalnets.brains.i_brain import IBrain, IBrainCfg


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class IndirectEncodedCTRNNCfg(IBrainCfg):
    ffnn_config: dict
    ctrnn_config: dict
    number_dimensions: int
    red_z: float = 1.3
    green_z: float = 1.6
    blue_z: float = 1.9
    outputs_radius: float = 0.45
    outputs_z: float = -0.5


class IndirectCTRNN(IBrain):

    def __init__(self, individual: np.ndarray, configuration: dict, brain_state: dict,
                 env_observation_size: int, env_action_size: int,
                 ob_mean: Optional[np.ndarray], ob_std: Optional[np.ndarray]):
        super().__init__(
            individual, configuration, brain_state, env_observation_size, env_action_size,
            ob_mean, ob_std
        )

        self.config = IndirectEncodedCTRNNCfg(**configuration)

        cppn_size = FeedForwardNN.get_individual_size(input_size=2*self.config.number_dimensions,
                                                      output_size=1,
                                                      configuration=self.config.ffnn_config,
                                                      brain_state={})

        v_mask = brain_state["v_mask"]
        w_mask = brain_state["w_mask"]
        t_mask = brain_state["t_mask"]
        cppn_inputs_w = brain_state["cppn_inputs_w"]

        index = 0
        individual_v, index = self.read_matrix_from_genome(individual, index, np.count_nonzero(v_mask), 1)
        individual_w, index = self.read_matrix_from_genome(individual, index, cppn_size, 1)
        individual_t, index = self.read_matrix_from_genome(individual, index, np.count_nonzero(t_mask), 1)

        self.cppn = FeedForwardNN(input_size=2*self.config.number_dimensions,
                                  output_size=1,
                                  individual=individual_w,
                                  configuration=self.config.ffnn_config,
                                  brain_state={})

        individual_ctrnn_v = individual_v.flatten()
        individual_ctrnn_w = self.cppn.predict(cppn_inputs_w).flatten()
        individual_ctrnn_t = individual_t.flatten()

        individual_ctrnn = np.concatenate((individual_ctrnn_v, individual_ctrnn_w, individual_ctrnn_t))

        brain_state_ctrnn = {"v_mask": v_mask, "w_mask": w_mask, "t_mask": t_mask}

        # TODO check if this works regarding env_observation_size and env_action_size. I guess the CTRNN config
        #   needs to be careful with which enhancer they use, if any, since when creating the CTRNN here an enhancer
        #   is created if this is provided in the config.
        self.ctrnn = CTRNN(individual_ctrnn, self.config.ctrnn_config, brain_state_ctrnn, env_observation_size,
                           env_action_size)

    def internal_step(self, ob: np.ndarray) -> Union[np.ndarray, np.generic]:

        # assert ob.ndim == 3
        # assert ob.shape == self.input_size
        assert ob.ndim == 1

        # ob = self.get_input_vector_from_observation(ob)

        # assert ob.ndim == 1

        # TODO enhancer_info is thrown away here, since IBrain expects one output from internal_step. If this brain is
        #  used in the future, IBrain.step() should maybe be extended to also accept the enhancer_info from this brain
        ctrnn_action, _ = self.ctrnn.step(ob)

        return ctrnn_action

    def reset(self, rng_seed: int):
        super().reset(rng_seed)

        self.ctrnn.reset(rng_seed)

    @classmethod
    def generate_brain_state(cls, input_size: int, output_size: int, configuration: dict):

        config = IndirectEncodedCTRNNCfg(**configuration)

        CTRNN.generate_brain_state(input_size, output_size, config.ctrnn_config)

        # TODO: This should later not be hard coded
        input_image_width = 64
        input_image_height = 64

        red_z = config.red_z
        green_z = config.green_z
        blue_z = config.blue_z
        outputs_radius = config.outputs_radius
        outputs_z = config.outputs_z

        input_positions = cls.get_rgb_positions(input_image_width, input_image_height, red_z, green_z, blue_z)
        neuron_positions = np.random.random((config.ctrnn_config['number_neurons'], config.number_dimensions))
        output_positions = cls.get_circle_positions(output_size, outputs_radius, outputs_z)

        brain_state_ctrnn = CTRNN.generate_brain_state(input_size, output_size, config.ctrnn_config)

        # individual_size_ctrnn = ContinuousTimeRNN.get_individual_size(input_size, output_size, config.ctrnn_config,
        #                                                              brain_state_ctrnn)

        # assert individual_size_ctrnn == len(input_positions) * len(neuron_positions) + len(
        #     neuron_positions) * len(neuron_positions) + len(neuron_positions) * len(output_positions)

        cppn_inputs_v = np.zeros((len(input_positions) * len(neuron_positions), 3+config.number_dimensions))
        cppn_inputs_w = np.zeros((len(neuron_positions) * len(neuron_positions), 2*config.number_dimensions))
        cppn_inputs_t = np.zeros((len(output_positions) * len(neuron_positions), 3+config.number_dimensions))

        # Decode V using cppn
        index_v = 0
        for i in range(len(neuron_positions)):
            for j in range(len(input_positions)):
                cppn_inputs_v[index_v] = np.concatenate((input_positions[j], neuron_positions[i]))
                index_v += 1

        # Decode W using cppn
        index_w = 0
        for i in range(len(neuron_positions)):
            for j in range(len(neuron_positions)):
                cppn_inputs_w[index_w] = np.concatenate((neuron_positions[j], neuron_positions[i]))
                index_w += 1

        # Decode T using cppn
        index_t = 0
        for i in range(len(output_positions)):
            for j in range(len(neuron_positions)):
                cppn_inputs_t[index_t] = np.concatenate((neuron_positions[j], output_positions[i]))
                index_t += 1

        # assert index_v + index_w + index_t == individual_size_ctrnn

        cppn_inputs_v = cppn_inputs_v.reshape(-1, 3+config.number_dimensions, 1)
        cppn_inputs_w = cppn_inputs_w.reshape(-1, 2*config.number_dimensions, 1)
        cppn_inputs_t = cppn_inputs_t.reshape(-1, 3+config.number_dimensions, 1)

        v_mask = brain_state_ctrnn['v_mask']
        w_mask = brain_state_ctrnn['w_mask']
        t_mask = brain_state_ctrnn['t_mask']

        return cls.get_brain_state_from_arrays(v_mask, w_mask, t_mask,
                                               input_positions, neuron_positions, output_positions,
                                               cppn_inputs_v, cppn_inputs_w, cppn_inputs_t)

    @classmethod
    def register_brain_state_for_saving(cls, model_contents: dict, brain_state: Dict[str, np.ndarray]):
        v_mask = brain_state['v_mask']
        w_mask = brain_state['w_mask']
        t_mask = brain_state['t_mask']
        input_positions = brain_state['input_positions']
        neuron_positions = brain_state['neuron_positions']
        output_positions = brain_state['output_positions']
        cppn_inputs_v = brain_state['cppn_inputs_v']
        cppn_inputs_w = brain_state['cppn_inputs_w']
        cppn_inputs_t = brain_state['cppn_inputs_t']

        model_contents["brain_state_v_mask"] = v_mask
        model_contents["brain_state_w_mask"] = w_mask
        model_contents["brain_state_t_mask"] = t_mask

        model_contents["brain_state_input_positions"] = input_positions
        model_contents["brain_state_neuron_positions"] = neuron_positions
        model_contents["brain_state_output_positions"] = output_positions

        model_contents["brain_state_cppn_inputs_v"] = cppn_inputs_v
        model_contents["brain_state_cppn_inputs_w"] = cppn_inputs_w
        model_contents["brain_state_cppn_inputs_t"] = cppn_inputs_t

        return model_contents

    @classmethod
    def load_brain_state(cls, brain_data) -> Optional[Dict[str, np.ndarray]]:
        v_mask = brain_data["brain_state_v_mask"]
        w_mask = brain_data["brain_state_w_mask"]
        t_mask = brain_data["brain_state_t_mask"]

        input_positions = brain_data["brain_state_input_positions"]
        neuron_positions = brain_data["brain_state_neuron_positions"]
        output_positions = brain_data["brain_state_output_positions"]

        cppn_inputs_v = brain_data["brain_state_cppn_inputs_v"]
        cppn_inputs_w = brain_data["brain_state_cppn_inputs_w"]
        cppn_inputs_t = brain_data["brain_state_cppn_inputs_t"]

        return cls.get_brain_state_from_arrays(v_mask, w_mask, t_mask,
                                               input_positions, neuron_positions, output_positions,
                                               cppn_inputs_v, cppn_inputs_w, cppn_inputs_t)

    @staticmethod
    def get_brain_state_from_arrays(v_mask, w_mask, t_mask, input_positions, neuron_positions,
                                    output_positions, cppn_inputs_v, cppn_inputs_w, cppn_inputs_t):

        brain_state = dict()
        brain_state['v_mask'] = v_mask
        brain_state['w_mask'] = w_mask
        brain_state['t_mask'] = t_mask
        brain_state['input_positions'] = input_positions
        brain_state['neuron_positions'] = neuron_positions
        brain_state['output_positions'] = output_positions
        brain_state['cppn_inputs_v'] = cppn_inputs_v
        brain_state['cppn_inputs_w'] = cppn_inputs_w
        brain_state['cppn_inputs_t'] = cppn_inputs_t

        return brain_state

    @staticmethod
    def get_rgb_positions(width: int, height: int,
                          red_position_z: float, green_position_z: float, blue_position_z: float) -> np.ndarray:
        space_x = np.linspace(0, 1, width)
        space_y = np.linspace(0, 1, height)

        grid_x, grid_y = np.meshgrid(space_x, space_y)
        rgb_positions_x = grid_x.flatten()
        rgb_positions_y = grid_y.flatten()

        red_positions = np.column_stack(
            (rgb_positions_x, rgb_positions_y, np.ones(width * height) * red_position_z))
        green_positions = np.column_stack(
            (rgb_positions_x, rgb_positions_y, np.ones(width * height) * green_position_z))
        blue_positions = np.column_stack(
            (rgb_positions_x, rgb_positions_y, np.ones(width * height) * blue_position_z))

        return np.vstack((red_positions, green_positions, blue_positions))

    @staticmethod
    def get_circle_positions(number_positions: int, radius: float, position_z: float) -> np.ndarray:
        circle_positions_x = np.zeros(number_positions)
        circle_positions_y = np.zeros(number_positions)

        angles = np.linspace(0, 2 * np.pi, number_positions, endpoint=False)

        for i in range(number_positions):
            circle_positions_x[i] = radius * np.cos(angles[i]) + 0.5
            circle_positions_y[i] = radius * np.sin(angles[i]) + 0.5

        circle_positions_z = np.ones(number_positions) * position_z

        return np.column_stack((circle_positions_x, circle_positions_y, circle_positions_z))

    @staticmethod
    def get_input_vector_from_observation(observation: np.ndarray) -> np.ndarray:

        observation_red = observation[:, :, 0].flatten()
        observation_green = observation[:, :, 1].flatten()
        observation_blue = observation[:, :, 2].flatten()

        return np.concatenate((observation_red, observation_green, observation_blue))

    @staticmethod
    def keep_highest_absolute_values_inplace(array: np.ndarray, percentage: float):

        assert array.ndim == 1

        number_of_lowest_values = round((1-percentage)*len(array))

        # Find the lowest absolute elements
        # https://stackoverflow.com/questions/34226400/find-the-index-of-the-k-smallest-values-of-a-numpy-array
        indizes = np.argpartition(abs(array), number_of_lowest_values)[:number_of_lowest_values]

        # Set these elements to zero
        array[indizes] = 0

        return

    @classmethod
    def get_free_parameter_usage(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):

        config = IndirectEncodedCTRNNCfg(**configuration)

        free_parameters_cppn = FeedForwardNN.get_individual_size(input_size=2*config.number_dimensions,
                                                                 output_size=1,
                                                                 configuration=config.ffnn_config,
                                                                 brain_state={})

        v_mask = brain_state['v_mask']
        t_mask = brain_state['t_mask']

        free_parameters_v = np.count_nonzero(v_mask)
        free_parameters_t = np.count_nonzero(t_mask)

        return {'V': free_parameters_v, 'CPPN': free_parameters_cppn, 'T': free_parameters_t}

    @classmethod
    def get_individual_size(cls, input_size: int, output_size: int, configuration: dict, brain_state: dict):

        individual_size = 0
        free_parameter_usage = cls.get_free_parameter_usage(input_size, output_size, configuration, brain_state)

        for free_parameters in free_parameter_usage.values():
            individual_size += free_parameters

        return individual_size
