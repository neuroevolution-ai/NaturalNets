import copy
import multiprocessing as mp
import os
import time

import gym
import numpy as np
import torch
from gym.spaces import flatdim
from procgen import ProcgenGym3Env

from autoencoder.conv_unpool import ConvUnpoolAutoencoder


# print("Setting number of Torch threads and interop threads to 1.")
# torch.set_num_threads(1)
# torch.set_num_interop_threads(1)


class EpisodeRunnerAutoEncoder:

    def __init__(self, environment: dict, brain_class, brain_configuration: dict, use_gpu: bool = True):

        if use_gpu and torch.cuda.is_available():
            self.device = torch.device('cuda')
            self.map_location = "cuda:0"
        else:
            if use_gpu:
                print("Warning: use_gpu set to True but CUDA device not found, continuing with CPU")
            self.device = torch.device('cpu')
            self.map_location = self.device

        self.autoencoder = ConvUnpoolAutoencoder()
        self.autoencoder.load_state_dict(torch.load("autoencoder/Conv_Unpool.pt", self.map_location))
        self.autoencoder.to(self.device)
        self.autoencoder.eval()

        self.env_name = environment["name"]
        self.distribution_mode = environment["distribution_mode"]
        env = gym.make(self.env_name, distribution_mode=self.distribution_mode)
        self.input_size = 32 * 6 * 6
        self.output_size = flatdim(env.action_space)

        self.brain_class = brain_class
        self.brain_configuration = brain_configuration

        self.brain_state = brain_class.generate_brain_state(input_size=self.input_size,
                                                            output_size=self.output_size,
                                                            configuration=brain_configuration)

    def preprocess_ob(self, ob):
        return np.transpose(ob, (0, 3, 1, 2)) / 255.0

    def transform_ob(self, ob: np.ndarray) -> np.ndarray:
        ob = self.preprocess_ob(ob)
        with torch.no_grad():
            ob = torch.from_numpy(ob).float().to(self.device)
            ob = self.autoencoder.encode(ob)
            # Move back to memory first, this is required when converting Tensor that is on CUDA device
            ob_cpu = ob.cpu().clone().numpy()
            del ob
            torch.cuda.empty_cache()
            return ob_cpu

    def get_individual_size(self):
        return self.brain_class.get_individual_size(input_size=self.input_size, output_size=self.output_size,
                                                    configuration=self.brain_configuration,
                                                    brain_state=self.brain_state)

    def get_input_size(self):
        return self.input_size

    def get_output_size(self):
        return self.output_size

    def save_brain_state(self, path):
        self.brain_class.save_brain_state(path, self.brain_state)

    def get_free_parameter_usage(self):
        return self.brain_class.get_free_parameter_usage(input_size=self.input_size, output_size=self.output_size,
                                                         configuration=self.brain_configuration,
                                                         brain_state=self.brain_state)

    def get_actions(self, brain, ob):
        return brain.step(ob.flatten())

    def calculate_actions_trivial(self, brains, obs):
        actions = [brain.step(ob.flatten()) for (brain, ob) in zip(brains, obs)]
        return actions

    def eval_fitness(self, evaluations, episode_steps: int = 500, break_all_episodes: bool = False):
        """

        :param evaluations: List of 3-tuples (individual, env_seed, number_of_rounds)
        :param episode_steps: Number of steps per episode
        :param break_all_episodes: When one episode is done, break all episodes
        :return:
        """
        # Extract parameters, this list of lists is necessary since pool.map only accepts a single argument
        # See here: http://python.omics.wiki/multiprocessing_map/multiprocessing_partial_function_multiple_arguments
        # individual = evaluations[0]
        env_seed = evaluations[0][1]
        number_of_rounds = evaluations[0][2]

        brains = []
        for single_evaluation in evaluations:
            brains.append(self.brain_class(input_size=self.input_size, output_size=self.output_size,
                                           individual=single_evaluation[0], configuration=self.brain_configuration,
                                           brain_state=self.brain_state))

        fitness_total = 0
        times_episodes = []
        for i in range(number_of_rounds):
            # num_threads=8 can be set here, don't know how it effects performance yet
            env = ProcgenGym3Env(num=len(evaluations), env_name="heist", use_backgrounds=False,
                                 distribution_mode=self.distribution_mode, num_levels=1, start_level=env_seed + i)

            rew, ob, first = env.observe()
            observations = ob["rgb"]
            ob = self.transform_ob(observations)

            # print(torch.cuda.memory_summary(device=self.device))
            # print("Memory: {}".format(torch.cuda.memory_allocated(device=self.device)))

            # pool = mp.get_context("spawn").Pool(processes=os.cpu_count())

            fitness_current = [0] * len(evaluations)
            # times_actions = []

            time_s = time.time()
            for i in range(episode_steps):

                # actions = pool.starmap(self.get_actions, zip(brains, ob))
                # time_actions_s = time.time()
                actions = self.calculate_actions_trivial(brains, ob)
                # times_actions.append(time.time() - time_actions_s)
                actions = np.argmax(actions, axis=1)

                env.act(actions)
                rew, ob, first = env.observe()

                if any(first) and break_all_episodes:
                    print("break_episodes: One or more environments are done, stopping all episodes")
                    break

                observations = ob["rgb"]
                ob = self.transform_ob(observations)
                # print(torch.cuda.memory_summary(device=self.device))
                # print("Memory: {}".format(torch.cuda.memory_allocated(device=self.device)))

                # if i > 10:
                #     break

                fitness_current += rew
            print("Episodes with VecEnv finished")
            # print("Times actions Mean {}".format(np.mean(times_actions)))
            # print("Times actions Std {}".format(np.std(times_actions)))
            # print("Times actions Max {}".format(np.max(times_actions)))
            # print("Times actions Min {}".format(np.min(times_actions)))
            times_episodes.append(time.time() - time_s)
            # break
            fitness_total += fitness_current

        return fitness_total / number_of_rounds, times_episodes

    def _validate_genome(self, validation_triple, episode_steps: int = 500, break_all_episodes: bool = False):
        validation_genome = validation_triple[0]
        validation_seed = validation_triple[1]

        brain = self.brain_class(input_size=self.input_size, output_size=self.output_size,
                                 individual=validation_genome, configuration=self.brain_configuration,
                                 brain_state=self.brain_state)

        env = gym.make(self.env_name,
                       num_levels=1,
                       start_level=validation_seed,
                       distribution_mode=self.distribution_mode)
        ob = env.reset()
        ob = np.expand_dims(ob, axis=0)
        ob = self.transform_ob(ob)

        fitness = 0
        done = False

        time_s = time.time()
        while not done:
            action = brain.step(ob.flatten())
            ob, rew, done, info = env.step(np.argmax(action))

            ob = np.expand_dims(ob, axis=0)
            ob = self.transform_ob(ob)

            fitness += rew

        return [fitness, time.time() - time_s]

    def validate_fitness(self, evaluations, episode_steps: int = 500, break_all_episodes: bool = False):
        """

        :param evaluations: List of 3-tuples (individual, env_seed, number_of_rounds)
        :param episode_steps: Number of steps per episode
        :param break_all_episodes: When one episode is done, break all episodes
        :return:
        """
        old_device = self.device
        old_map_location = self.map_location

        self.device = torch.device('cpu')
        self.map_location = self.device

        validation_fitnesses = []
        validation_episode_times = []

        list_episode_steps = [episode_steps] * len(evaluations)
        list_break_all_episodes = [break_all_episodes] * len(evaluations)

        with mp.Pool() as pool:
            validation_results = pool.starmap(self._validate_genome,
                                              zip(evaluations, list_episode_steps, list_break_all_episodes))

        for result in validation_results:
            validation_fitnesses.append(result[0])
            validation_episode_times.append(result[1])

        self.device = old_device
        self.map_location = old_map_location

        return validation_fitnesses, validation_episode_times
