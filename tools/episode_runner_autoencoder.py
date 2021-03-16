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

    def transform_ob(self, ob):
        with torch.no_grad():
            ob = self.preprocess_ob(ob)
            ob = ob.to(self.device)
            ob = self.autoencoder.encode(ob)
            # Move back to memory first, this is required when converting Tensor that is on CUDA device
            return ob

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
            observations = copy.deepcopy(ob["rgb"])
            ob = self.transform_ob(observations)

            pool = mp.get_context("spawn").Pool(processes=os.cpu_count())

            fitness_current = [0] * len(evaluations)

            time_s = time.time()
            for i in range(episode_steps):

                actions = pool.starmap(self.get_actions, zip(brains, ob))
                actions = np.argmax(actions, axis=1)

                env.act(actions)
                rew, ob, first = env.observe()

                if any(first) and break_all_episodes:
                    print("break_episodes: One or more environments are done, stopping all episodes")
                    break

                ob = self.transform_ob(ob["rgb"])
                fitness_current += rew

            times_episodes.append(time.time() - time_s)

            fitness_total += fitness_current

        return fitness_total / number_of_rounds, times_episodes
