import attr
import gym
import numpy as np
from gym.spaces import flatdim


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class EnvironmentCfg:
    name: str
    distribution_mode: str


class EpisodeRunner:

    def __init__(self, env_configuration: dict, brain_class, brain_configuration: dict):

        self.env_config = EnvironmentCfg(**env_configuration)

        env = gym.make(self.env_config.name, distribution_mode=self.env_config.distribution_mode)
        self.input_size = flatdim(env.observation_space)
        self.output_size = flatdim(env.action_space)

        self.brain_class = brain_class
        self.brain_configuration = brain_configuration

        self.brain_state = brain_class.generate_brain_state(input_size=self.input_size,
                                                            output_size=self.output_size,
                                                            configuration=brain_configuration)

    def get_individual_size(self):
        return self.brain_class.get_individual_size(self.input_size, self.output_size, self.brain_configuration,
                                                    self.brain_state)

    def get_input_size(self):
        return self.input_size

    def get_output_size(self):
        return self.output_size

    def save_brain_state(self, path):
        self.brain_class.save_brain_state(path, self.brain_state)

    def get_free_parameter_usage(self):
        return self.brain_class.get_free_parameter_usage(self.input_size, self.output_size, self.brain_configuration,
                                                         self.brain_state)

    def eval_fitness(self, evaluation):

        # Extract parameters, this list of lists is necessary since pool.map only accepts a single argument
        # See here: http://python.omics.wiki/multiprocessing_map/multiprocessing_partial_function_multiple_arguments
        individual = evaluation[0]
        env_seed = evaluation[1]
        number_of_rounds = evaluation[2]

        brain = self.brain_class(individual=individual,
                                 configuration=self.brain_configuration,
                                 brain_state=self.brain_state)

        fitness_total = 0

        for i in range(number_of_rounds):

            env = gym.make(self.env_config.name,
                           num_levels=1,
                           start_level=env_seed+i,
                           distribution_mode=self.env_config.distribution_mode)
            ob = env.reset()
            brain.reset()

            fitness_current = 0
            done = False

            while not done:

                # obs = cv2.resize(ob, (16, 16), interpolation=cv2.INTER_AREA)

                action = brain.step(ob.flatten()/255.0)
                ob, rew, done, info = env.step(np.argmax(action))
                fitness_current += rew

            fitness_total += fitness_current

        return fitness_total / number_of_rounds
