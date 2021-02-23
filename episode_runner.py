import gym
from gym.spaces import flatdim
from continuous_time_rnn import *


class EpisodeRunner:

    def __init__(self, number_neurons, v_mask_param, w_mask_param, t_mask_param, delta_t, clipping_range_min, clipping_range_max, env_name, number_of_rounds):

        self.env_name = env_name
        env = gym.make(env_name)
        number_inputs = flatdim(env.observation_space)
        number_outputs = flatdim(env.action_space)

        self.number_of_rounds = number_of_rounds
        self.number_neurons = number_neurons
        self.delta_t = delta_t
        self.clipping_range_min = clipping_range_min
        self.clipping_range_max = clipping_range_max

        self.env_seed = 100

        self.v_mask, self.w_mask, self.t_mask = ContinuousTimeRNN.generate_masks(number_inputs=number_inputs,
                                                                                 number_neurons=number_neurons,
                                                                                 number_outputs=number_outputs,
                                                                                 v_mask_param=v_mask_param,
                                                                                 w_mask_param=w_mask_param,
                                                                                 t_mask_param=t_mask_param)

    def get_individual_size(self):
        return ContinuousTimeRNN.get_individual_size(v_mask=self.v_mask, w_mask=self.w_mask, t_mask=self.t_mask)

    def eval_fitness(self, individual):



        brain = ContinuousTimeRNN(individual=individual,
                                  delta_t=self.delta_t,
                                  number_neurons=self.number_neurons,
                                  v_mask=self.v_mask,
                                  w_mask=self.w_mask,
                                  t_mask=self.t_mask,
                                  clipping_range_min=self.clipping_range_min,
                                  clipping_range_max=self.clipping_range_max)

        fitness_total = 0

        for i in range(self.number_of_rounds):

            env = gym.make(self.env_name, num_levels=1, start_level=self.env_seed+i, distribution_mode="memory")
            ob = env.reset()
            brain.reset()

            fitness_current = 0
            done = False

            while not done:
                action = brain.step(ob.flatten()/255.0)
                ob, rew, done, info = env.step(np.argmax(action))
                fitness_current += rew

            fitness_total += fitness_current

        return fitness_total / self.number_of_rounds
