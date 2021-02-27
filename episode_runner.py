import gym
from gym.spaces import flatdim
from brains.continuous_time_rnn import *


class EpisodeRunner:

    def __init__(self, env_name: str, brain_configuration: dict):

        self.env_name = env_name
        env = gym.make(env_name)

        self.brain_configuration = brain_configuration

        self.brain_state = ContinuousTimeRNN.generate_brain_state(number_inputs=flatdim(env.observation_space),
                                                                  number_outputs=flatdim(env.action_space),
                                                                  configuration=brain_configuration)

    def get_individual_size(self):
        return ContinuousTimeRNN.get_individual_size(self.brain_state)

    def save_brain_state(self, path):
        ContinuousTimeRNN.save_brain_state(path, self.brain_state)

    def eval_fitness(self, evaluation):

        # Extract parameters, this list of lists is necessary since pool.map only accepts a single argument
        # See here: http://python.omics.wiki/multiprocessing_map/multiprocessing_partial_function_multiple_arguments
        individual = evaluation[0]
        env_seed = evaluation[1]
        number_of_rounds = evaluation[2]

        brain = ContinuousTimeRNN(individual=individual, configuration=self.brain_configuration,
                                  brain_state=self.brain_state)

        fitness_total = 0

        for i in range(number_of_rounds):

            env = gym.make(self.env_name, num_levels=1, start_level=env_seed+i, distribution_mode="memory")
            ob = env.reset()
            brain.reset()

            fitness_current = 0
            done = False

            while not done:
                action = brain.step(ob.flatten()/255.0)
                ob, rew, done, info = env.step(np.argmax(action))
                fitness_current += rew

            fitness_total += fitness_current

        return fitness_total / number_of_rounds
