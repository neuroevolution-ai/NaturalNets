import math
import time
from episode_runner import *
import multiprocessing
import numpy as np
import random

pool = multiprocessing.Pool()

# Optimize parameters
number_generations = 500

# Offspring population size (lambda)
offspring_population_size = 798

# Parent population size (mu)
parent_population_size = 50

# Mutation step size (sigma)
step_size = 0.05

number_of_validation_runs = 50
number_of_rounds = 5


def get_reward_weights(population_size):

    mu = population_size

    w_denominator = 0
    for j in range(mu):
        w_denominator += math.log(mu + 0.5) - math.log(j + 1)

    w = np.asarray([(math.log(mu + 0.5) - math.log(i + 1)) / w_denominator for i in range(mu)])

    return w


w = get_reward_weights(parent_population_size)

# Initialize episode runner
ep_runner = EpisodeRunner(env_name='procgen:procgen-heist-v0',
                          number_neurons=200,
                          v_mask_param=0.001,
                          w_mask_param=0.05,
                          t_mask_param=0.1,
                          delta_t=0.05,
                          clipping_range_min=-1,
                          clipping_range_max=1)

individual_size = ep_runner.get_individual_size()

print("Individual size: {}".format(individual_size))

# Initial genome
policy = np.zeros(individual_size)

for gen in range(number_generations):

    t_start = time.time()

    # Environment seed for this generation (excludes validation env seeds)
    env_seed = random.randint(number_of_validation_runs, 100000)

    # Initialize genomes
    evaluations = []
    genomes = []
    for _ in range(offspring_population_size):
        genome = policy + step_size * np.random.randn(individual_size).astype(np.float32)
        genomes.append(genome)
        evaluations.append([genome, env_seed, number_of_rounds])

    # Evaluate candidates
    rewards = pool.map(ep_runner.eval_fitness, evaluations)
    # reward = ep_runner.eval_fitness(genomes[0])

    # Sort rewards in descending order
    sorted_rewards = np.flip(np.argsort(rewards)).flatten()

    # Update policy
    for i in range(parent_population_size):
        j = sorted_rewards[i]
        policy += step_size * w[i] * genomes[j]

    # Save policy
    np.save('policy.npy', policy)

    print("Generation: {}   Min: {:4.2f}   Mean: {:4.2f}   Max: {:4.2f}   Elapsed time:  {:4.2f}s ".format(gen,
                                                                                                       np.min(rewards),
                                                                                                       np.mean(rewards),
                                                                                                       np.max(rewards),
                                                                                                       time.time() - t_start))
