from typing import Optional, Dict

import numpy as np
from attrs import define, field, validators

from naturalnets.brains.i_brain import get_brain_class
from naturalnets.environments.i_environment import IEnvironment, register_environment_class


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class ChallengerNeuralNetworkCfg:
    type: str = field(validator=validators.instance_of(str))
    number_inputs: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    number_outputs: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    exclude_reward_from_observation: bool = field(validator=validators.instance_of(bool))
    number_time_steps: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    brain: dict


@register_environment_class
class ChallengerNeuralNetwork(IEnvironment):

    def __init__(self, configuration: dict, **kwargs):
        self.config = ChallengerNeuralNetworkCfg(**configuration)

        self.brain = None
        self.t = 0

    def get_number_inputs(self):
        return self.config.number_inputs

    def get_number_outputs(self):
        return self.config.number_outputs

    def reset(self, env_seed: int):
        rng = np.random.default_rng(seed=env_seed)

        # Get brain class from configuration
        brain_class = get_brain_class(self.config.brain["type"])
        brain_configuration = self.config.brain

        number_inputs_challenger_nn = self.config.number_outputs
        number_outputs_challenger_nn = self.config.number_inputs

        brain_state = brain_class.generate_brain_state(
            number_inputs_challenger_nn, number_outputs_challenger_nn, brain_configuration)

        individual_size = brain_class.get_individual_size(
            number_inputs_challenger_nn, number_outputs_challenger_nn, brain_configuration, brain_state)

        individual = rng.standard_normal(individual_size, dtype=np.float32)

        self.brain = brain_class(input_size=number_inputs_challenger_nn,
                                 output_size=number_outputs_challenger_nn,
                                 individual=individual,
                                 configuration=brain_configuration,
                                 brain_state=brain_state)

        self.t = 0

        return np.zeros(self.config.number_inputs)

    def step(self, action: np.ndarray):

        ob = self.brain.step(action)

        rew = ob[0] / float(self.config.number_time_steps)

        if self.config.exclude_reward_from_observation:
            ob[0] = 0.0

        self.t += 1

        if self.t < self.config.number_time_steps:
            done = False
        else:
            done = True

        return ob, rew, done, {}

    def render(self, enhancer_info: Optional[Dict[str, np.ndarray]]):
        raise NotImplementedError("Rendering is not implemented for this environment")
