import os
import time
from typing import Type, List, Tuple

import numpy as np
from attrs import define, field, validators

from naturalnets.brains import IBrain
from naturalnets.enhancers.i_enhancer import get_enhancer_class
from naturalnets.tools.utils import RunningStat

MODEL_FILE_NAME = "model.npz"
INDIVIDUAL_KEY = "individual"
OB_MEAN_KEY = "ob_mean"
OB_STD_KEY = "ob_std"


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class PreprocessingCfg:
    observation_standardization: bool = field(default=False, validator=validators.instance_of(bool))
    calc_ob_stat_prob: float = field(
        default=0.0,
        converter=float,
        validator=[validators.instance_of(float), validators.ge(0.0), validators.le(1.0)]
    )

    observation_clipping: bool = field(default=False, validator=validators.instance_of(bool))
    ob_clipping_value: float = field(
        default=0.0,
        converter=float,
        validator=[validators.instance_of(float), validators.ge(0.0)]
    )


class EpisodeRunner:

    def __init__(self, env_class, env_configuration: dict, brain_class: Type[IBrain], brain_configuration: dict,
                 preprocessing_config: dict, enhancer_config: dict, global_seed: int):

        self.env_class = env_class
        self.env_configuration = env_configuration
        env = self.env_class(configuration=self.env_configuration)

        self.env_observation_size = env.get_number_inputs()
        self.env_action_size = env.get_number_outputs()

        self.brain_configuration = brain_configuration
        self.brain_class = brain_class

        self.input_size = self.env_observation_size
        self.output_size = self.env_action_size

        self.enhancer_class = get_enhancer_class(enhancer_config["type"])
        enhancer = self.enhancer_class(env_output_size=self.env_action_size)

        self.output_size += enhancer.get_number_outputs()

        self.brain_state = brain_class.generate_brain_state(
            input_size=self.input_size,
            output_size=self.output_size,
            configuration=self.brain_configuration
        )

        self.preprocessing_config = PreprocessingCfg(**preprocessing_config)

        self.current_ob_mean, self.current_ob_std = None, None
        if self.preprocessing_config.observation_standardization:
            self.obs_rng = np.random.default_rng(global_seed)

            self.ob_stat = RunningStat(
                shape=(self.env_observation_size,),
                eps=1e-2  # eps to prevent dividing by zero at the beginning when computing mean/stdev
            )

            self.current_ob_mean = self.ob_stat.mean
            self.current_ob_std = self.ob_stat.std

    def get_individual_size(self) -> Tuple[int, int, int]:
        """
        Calculates the individual size for the brain, and the number of output neurons in that individual

        :return: Individual size and number of output neurons
        """
        return self.brain_class.get_individual_size(self.input_size, self.output_size, self.brain_configuration,
                                                    self.brain_state)

    def get_input_size(self):
        return self.input_size

    def get_output_size(self):
        return self.output_size

    def get_free_parameter_usage(self):
        free_parameter_usage, _, _ = self.brain_class.get_free_parameter_usage(
            self.input_size, self.output_size, self.brain_configuration, self.brain_state)
        return free_parameter_usage

    def update_ob_mean_std(self, recorded_observations: List[np.ndarray]):
        if self.preprocessing_config.observation_standardization:
            for recorded_ob in recorded_observations:
                self.ob_stat.increment(
                    recorded_ob.sum(axis=0),
                    np.square(recorded_ob).sum(axis=0),
                    recorded_ob.shape[0]
                )

            self.current_ob_mean = self.ob_stat.mean
            self.current_ob_std = self.ob_stat.std

    def save_brain(self, results_subdirectory: str, individual: np.ndarray):
        file_name = os.path.join(results_subdirectory, MODEL_FILE_NAME)

        model_contents = {
            INDIVIDUAL_KEY: individual
        }

        model_contents = self.brain_class.register_brain_state_for_saving(model_contents, self.brain_state)

        if self.current_ob_mean is not None and self.current_ob_std is not None:
            model_contents[OB_MEAN_KEY] = self.current_ob_mean
            model_contents[OB_STD_KEY] = self.current_ob_std

        np.savez(file_name, **model_contents)

    def load_brain(self, exp_dir: str) -> np.ndarray:
        brain_data = np.load(os.path.join(exp_dir, MODEL_FILE_NAME))

        individual = brain_data[INDIVIDUAL_KEY]

        self.brain_state = self.brain_class.load_brain_state(brain_data)

        if OB_MEAN_KEY in brain_data and OB_STD_KEY in brain_data:
            self.current_ob_mean = brain_data[OB_MEAN_KEY]
            self.current_ob_std = brain_data[OB_STD_KEY]

        return individual

    def eval_fitness(self, individual: np.ndarray, env_seed: int, number_of_rounds: int, training: bool,
                     render: bool = False, lag: float = 0.0):
        brain = self.brain_class(
            input_size=self.input_size,
            output_size=self.output_size,
            individual=individual,
            configuration=self.brain_configuration,
            brain_state=self.brain_state
        )

        enhancer = self.enhancer_class(
            env_output_size=self.env_action_size
        )

        fitness_total = 0

        total_obs = []

        for i in range(number_of_rounds):
            save_obs, obs_list = False, []
            # Only save observations for training episodes, and not for validation episodes
            if self.preprocessing_config.observation_standardization and training:
                save_obs = self.obs_rng.uniform(0.0, 1.0) < self.preprocessing_config.calc_ob_stat_prob

            render_mode = "human" if render else None
            env = self.env_class(configuration=self.env_configuration, render_mode=render_mode)

            ob = env.reset(env_seed=env_seed+i)
            enhancer.reset(rng_seed=env_seed+i)
            brain.reset()

            fitness_current = 0
            done = False

            if save_obs:
                obs_list.append(ob)

            while not done:
                processed_obs = ob

                if self.preprocessing_config.observation_standardization:
                    processed_obs = (processed_obs - self.current_ob_mean) / self.current_ob_std

                if self.preprocessing_config.observation_clipping:
                    processed_obs = np.clip(
                        processed_obs,
                        -self.preprocessing_config.ob_clipping_value, +self.preprocessing_config.ob_clipping_value
                    )

                action = brain.step(processed_obs)
                enhanced_action, enhancer_info = enhancer.step(action)
                ob, rew, done, info = env.step(enhanced_action)

                fitness_current += rew

                if save_obs:
                    obs_list.append(ob)

                if render:
                    env.render(enhancer_info)
                    time.sleep(lag)

            fitness_total += fitness_current

            if save_obs:
                total_obs.append(np.array(obs_list, dtype=np.float32))

        if self.preprocessing_config.observation_standardization and len(total_obs) > 0 and training:
            return fitness_total / number_of_rounds, total_obs

        return fitness_total / number_of_rounds

    def visualize(self, exp_dir: str, number_visualization_episodes: int, lag: float):
        individual = self.load_brain(exp_dir)

        fitness_total = 0

        for env_seed in range(number_visualization_episodes):
            fitness_episode = self.eval_fitness(
                individual=individual,
                env_seed=env_seed,
                number_of_rounds=1,
                training=False,
                render=True,
                lag=lag
            )

            fitness_total += fitness_episode

            print(f"Seed: {env_seed}   Reward:  {fitness_episode:4.2f}")

        print(f"Reward mean: {fitness_total / number_visualization_episodes:4.2f}")
        print("Finished")
