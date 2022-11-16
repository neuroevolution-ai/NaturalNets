from typing import Type

from naturalnets.brains import IBrain


class EpisodeRunner:

    def __init__(self, env_class, env_configuration: dict, brain_class: Type[IBrain], brain_configuration: dict):

        self.env_class = env_class
        self.env_configuration = env_configuration
        env = self.env_class(configuration=self.env_configuration)

        self.env_observation_size = env.get_number_inputs()
        self.env_action_size = env.get_number_outputs()

        self.brain_configuration = brain_configuration
        self.brain_class = brain_class

        self.input_size, self.output_size = self.brain_class.get_input_and_output_size(
            configuration=self.brain_configuration,
            env_observation_size=self.env_observation_size,
            env_action_size=self.env_action_size
        )

        self.brain_state = brain_class.generate_brain_state(
            input_size=self.input_size,
            output_size=self.output_size,
            configuration=self.brain_configuration
        )

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

        brain = self.brain_class(
            individual=individual,
            configuration=self.brain_configuration,
            brain_state=self.brain_state,
            env_observation_size=self.env_observation_size,
            env_action_size=self.env_action_size
        )

        fitness_total = 0

        for i in range(number_of_rounds):
            env = self.env_class(configuration=self.env_configuration)
            ob = env.reset(env_seed=env_seed+i)
            brain.reset(rng_seed=env_seed+i)

            fitness_current = 0
            done = False

            while not done:
                action, _ = brain.step(ob)
                ob, rew, done, info = env.step(action)
                fitness_current += rew

            fitness_total += fitness_current

        return fitness_total / number_of_rounds
