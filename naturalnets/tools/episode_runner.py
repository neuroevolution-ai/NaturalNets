from typing import Type

import numpy as np

from naturalnets.enhancers.i_enhancer import IEnhancer


class EpisodeRunner:

    def __init__(self, env_class, env_configuration: dict, brain_class, brain_configuration: dict,
                 enhancer_class: Type[IEnhancer]):

        self.env_class = env_class
        self.env_configuration = env_configuration
        env = self.env_class(configuration=self.env_configuration)

        env_output_size = env.get_number_outputs()

        self.enhancer = enhancer_class(env_output_size=env_output_size)

        self.input_size = env.get_number_inputs()
        self.output_size = env_output_size + self.enhancer.get_number_outputs()

        self.brain_class = brain_class
        self.brain_configuration = brain_configuration

        self.observation_standardization = self.brain_configuration["observation_standardization"]

        self.brain_state = brain_class.generate_brain_state(input_size=self.input_size,
                                                            output_size=self.output_size,
                                                            configuration=self.brain_configuration)

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

        ob_mean, ob_std, calc_ob_stat_prob = None, None, None
        if self.observation_standardization:
            ob_mean = evaluation[3]
            ob_std = evaluation[4]
            calc_ob_stat_prob = evaluation[5]

        brain = self.brain_class(input_size=self.input_size,
                                 output_size=self.output_size,
                                 individual=individual,
                                 configuration=self.brain_configuration,
                                 brain_state=self.brain_state)

        fitness_total = 0

        total_obs = []

        for i in range(number_of_rounds):
            save_obs, obs = False, []
            if self.observation_standardization:
                save_obs = np.random.rand() < calc_ob_stat_prob

            env = self.env_class(configuration=self.env_configuration)
            ob = env.reset(env_seed=env_seed+i)
            brain.reset()
            self.enhancer.reset(rng_seed=env_seed+i)

            fitness_current = 0
            done = False

            if save_obs:
                obs.append(ob)

            while not done:
                processed_ob = ob
                if self.observation_standardization:
                    processed_ob = np.clip((ob - ob_mean) / ob_std, -5.0, 5.0)

                action = brain.step(processed_ob)
                action, _ = self.enhancer.step(action)
                ob, rew, done, info = env.step(action)
                fitness_current += rew

                if save_obs:
                    obs.append(ob)

            fitness_total += fitness_current

            if save_obs:
                total_obs.append(np.array(obs, dtype=np.float32))

        if self.observation_standardization and len(total_obs) > 0:
            return fitness_total / number_of_rounds, total_obs

        return fitness_total / number_of_rounds
