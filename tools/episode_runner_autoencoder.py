import gym
from procgen import ProcgenGym3Env
import gym3
import numpy as np
from gym.spaces import flatdim
import torch
import multiprocessing as mp

from autoencoder.conv_unpool import ConvUnpoolAutoencoder

# print("Setting number of Torch threads and interop threads to 1.")
# torch.set_num_threads(1)
# torch.set_num_interop_threads(1)


class EpisodeRunnerAutoEncoder:

    def __init__(self, env_name: str, brain_class, brain_configuration: dict, use_gpu=False):

        if use_gpu:
            self.device = torch.device('cuda')
            self.map_location = "cuda:0"
        else:
            self.device = torch.device('cpu')
            self.map_location = self.device

        self.autoencoder = ConvUnpoolAutoencoder()
        self.autoencoder.load_state_dict(torch.load("autoencoder/Conv_Unpool.pt", self.map_location))
        self.autoencoder.to(self.device)
        self.autoencoder.eval()

        self.env_name = env_name
        env = gym.make(env_name)
        self.input_size = 32 * 6 * 6
        self.output_size = flatdim(env.action_space)

        self.brain_class = brain_class
        self.brain_configuration = brain_configuration

        self.brain_state = brain_class.generate_brain_state(input_size=self.input_size,
                                                            output_size=self.output_size,
                                                            configuration=brain_configuration)

    def preprocess_ob(self, ob):
        with torch.no_grad():
            obs = torch.from_numpy(ob)
            obs = obs.permute(0, 3, 1, 2).to(torch.float32)
            obs = obs / 255.0

            # obs = np.transpose(ob, (2, 0, 1))
            # obs = obs.astype(np.float32)
            # obs = obs / 255
            # obs = torch.from_numpy(obs)
            # obs = obs.unsqueeze(0)
            return obs

    def transform_ob(self, ob):
        with torch.no_grad():
            obs = self.preprocess_ob(ob)
            obs = obs.to(self.device)
            obs = self.autoencoder.encode(obs)
            # obs = obs[0].detach().numpy()
            return obs

    def get_individual_size(self):
        return self.brain_class.get_individual_size(self.brain_state)

    def get_input_size(self):
        return self.input_size

    def get_output_size(self):
        return self.output_size

    def save_brain_state(self, path):
        self.brain_class.save_brain_state(path, self.brain_state)

    def get_free_parameter_usage(self):
        return self.brain_class.get_free_parameter_usage(self.brain_state)

    def get_actions(self, brain, ob):
        return brain.step(ob.flatten())

    def eval_fitness(self, evaluation):

        # print("Torch Threads: {}".format(torch.get_num_threads()))
        # print("Torch Interop Threads: {}".format(torch.get_num_interop_threads()))

        # Extract parameters, this list of lists is necessary since pool.map only accepts a single argument
        # See here: http://python.omics.wiki/multiprocessing_map/multiprocessing_partial_function_multiple_arguments
        # individual = evaluation[0]
        env_seed = evaluation[0][1]
        number_of_rounds = evaluation[0][2]

        brains = []
        for single_evaluation in evaluation:
            brains.append(self.brain_class(individual=single_evaluation[0], configuration=self.brain_configuration,
                                           brain_state=self.brain_state))

        fitness_total = 0

        for i in range(number_of_rounds):
            # env = gym.make(self.env_name) # , num_levels=1, start_level=env_seed+i, distribution_mode="hard")
            # env = gym.make(self.env_name, use_backgrounds=False, distribution_mode="memory")
            env = ProcgenGym3Env(num=len(evaluation), env_name="heist", use_backgrounds=False,
                                 distribution_mode="memory", num_levels=1, start_level=env_seed + i, num_threads=8)
            rew, ob, first = env.observe()
            ob = self.transform_ob(ob["rgb"])

            pool = mp.Pool(processes=8)

            # rewards = np.zeros(population_size)
            # for _ in range(number_env_steps):
            #     env.act(gym3.types_np.sample(env.ac_space, bshape=(env.num,)))
            #     rew, obs, first = env.observe()
            #
            #     rewards += rew
            # return rewards

            # ob = env.reset()
            # # brain.reset()
            #
            fitness_current = [0] * len(evaluation)
            # done = False

            for _ in range(1000):

                # actions = pool.starmap(self.get_actions, zip(brains, ob))
                # actions = np.argmax(actions, axis=1)
                # env.act(actions)
                env.act(gym3.types_np.sample(env.ac_space, bshape=(env.num,)))
                rew, ob, first = env.observe()

                ob = self.transform_ob(ob["rgb"])
                fitness_current += rew

                # action = brain.step(ob.flatten())
                # ob, rew, done, info = env.step(np.argmax(action))
                # ob = self.transform_ob(ob)
                # fitness_current += rew

            fitness_total += fitness_current

        return fitness_total / number_of_rounds
