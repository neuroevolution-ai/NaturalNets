import attr
import numpy as np

from brains.lstm import LstmNN
from brains.i_brain import get_brain_class
from environments.i_environment import IEnvironment, registered_environment_classes


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class ChallengerNeuralNetworkCfg:
    type: str
    number_inputs: int
    number_outputs: int
    number_time_steps: int
    brain: dict


class ChallengerNeuralNetwork(IEnvironment):

    def __init__(self, env_seed: int, configuration: dict):

        self.config = ChallengerNeuralNetworkCfg(**configuration)

        self.rs = np.random.RandomState(env_seed)

        # Get brain class from configuration
        brain_class = get_brain_class(self.config.brain['type'])
        brain_configuration = self.config.brain

        brain_state = brain_class.generate_brain_state(self.config.number_outputs, self.config.number_inputs, brain_configuration)

        individual_size = brain_class.get_individual_size(self.config.number_outputs, self.config.number_inputs, brain_configuration, brain_state) 

        individual = self.rs.randn(individual_size).astype(np.float32)

        self.brain = brain_class(input_size=self.config.number_outputs,
                                 output_size=self.config.number_inputs,
                                 individual=individual,
                                 configuration=brain_configuration,
                                 brain_state=brain_state)

        self.t = 0

    def get_number_inputs(self):
        return self.config.number_inputs

    def get_number_outputs(self):
        return self.config.number_outputs

    def reset(self):
        return np.zeros(self.config.number_inputs)

    def step(self, action: np.ndarray):

        ob = self.brain.step(action)

        rew = ob[0]

        self.t += 1

        if self.t < self.config.number_time_steps:
            done = False
        else:
            done = True

        info = dict()

        return ob, rew, done, info


# TODO: Do this registration via class decorator
registered_environment_classes['ChallengerNeuralNetwork'] = ChallengerNeuralNetwork
