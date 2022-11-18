from typing import Type, List

import numpy as np

from naturalnets.brains import IBrain
from naturalnets.optimizers.openai_es.openai_es_utils import RunningStat


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

        # Manage the observation standardization statistics here, because they need to be sampled during the episode
        # rollouts. In addition, in train.py the update of the mean and stddev needs to be triggered, which can be
        # done with the EpisodeRunner
        self.observation_standardization = self.brain_configuration["preprocessing"]["observation_standardization"]
        self.calc_ob_stat_prob = self.brain_configuration["preprocessing"]["calc_ob_stat_prob"]

        if self.observation_standardization:
            # TODO use global seed from training cfg here?
            self.obs_rng = np.random.default_rng()

            self.ob_stat = RunningStat(
                shape=(self.env_observation_size,),
                eps=1e-2  # eps to prevent dividing by zero at the beginning when computing mean/stdev
            )

            self.current_ob_mean = self.ob_stat.mean
            self.current_ob_std = self.ob_stat.std

    def get_individual_size(self):
        return self.brain_class.get_individual_size(self.input_size, self.output_size, self.brain_configuration,
                                                    self.brain_state)

    def get_input_size(self):
        return self.input_size

    def get_output_size(self):
        return self.output_size

    def get_free_parameter_usage(self):
        return self.brain_class.get_free_parameter_usage(self.input_size, self.output_size, self.brain_configuration,
                                                         self.brain_state)

    def update_ob_mean_std(self, recorded_observations: List[np.ndarray]):
        if self.observation_standardization:
            for recorded_ob in recorded_observations:
                self.ob_stat.increment(
                    recorded_ob.sum(axis=0),
                    np.square(recorded_ob).sum(axis=0),
                    recorded_ob.shape[0]
                )

            self.current_ob_mean = self.ob_stat.mean
            self.current_ob_std = self.ob_stat.std

    def save_brain(self, results_subdirectory: str, individual: np.ndarray):
        self.brain_class.save_brain(
            results_subdirectory=results_subdirectory,
            individual=individual,
            brain_state=self.brain_state,
            ob_mean=self.current_ob_mean,
            ob_std=self.current_ob_std
        )

    def eval_fitness(self, evaluation):
        # Extract parameters, this list of lists is necessary since pool.map only accepts a single argument
        # See here: http://python.omics.wiki/multiprocessing_map/multiprocessing_partial_function_multiple_arguments
        individual = evaluation[0]
        env_seed = evaluation[1]
        number_of_rounds = evaluation[2]
        training: bool = evaluation[3]

        brain = self.brain_class(
            individual=individual,
            configuration=self.brain_configuration,
            brain_state=self.brain_state,
            env_observation_size=self.env_observation_size,
            env_action_size=self.env_action_size,
            ob_mean=self.current_ob_mean if self.observation_standardization else None,
            ob_std=self.current_ob_std if self.observation_standardization else None
        )

        fitness_total = 0

        total_obs = []

        for i in range(number_of_rounds):
            save_obs, obs = False, []
            # Only save observations for training episodes, and not for validation episodes
            if self.observation_standardization and training:
                save_obs = self.obs_rng.uniform(0.0, 1.0) < self.calc_ob_stat_prob

            env = self.env_class(configuration=self.env_configuration)
            ob = env.reset(env_seed=env_seed+i)
            brain.reset(rng_seed=env_seed+i)

            fitness_current = 0
            done = False

            if save_obs:
                obs.append(ob)

            while not done:
                action, _ = brain.step(ob)
                ob, rew, done, info = env.step(action)
                fitness_current += rew

                if save_obs:
                    obs.append(ob)

            fitness_total += fitness_current

            if save_obs:
                total_obs.append(np.array(obs, dtype=np.float32))

        if self.observation_standardization and len(total_obs) > 0 and training:
            return fitness_total / number_of_rounds, total_obs

        return fitness_total / number_of_rounds
