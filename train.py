import time
import os
from episode_runner import *
import multiprocessing
import random
from optimizer.cma_es import *
from optimizer.canonical_es import *
from datetime import datetime

pool = multiprocessing.Pool()

# Optimize parameters
number_generations = 5

# Offspring population size (lambda)
offspring_population_size = 112

# Parent population size (mu)
parent_population_size = 50

# Mutation step size (sigma)
step_size = 0.05

number_validation_runs = 100
number_rounds = 5
maximum_env_seed = 100000

optimizer = "CMA-ES"

# Initialize episode runner
ep_runner = EpisodeRunner(env_name='procgen:procgen-heist-v0',
                          number_neurons=200,
                          v_mask_param=0.0005,
                          w_mask_param=0.05,
                          t_mask_param=0.1,
                          delta_t=0.05,
                          clipping_range_min=-1,
                          clipping_range_max=1)

best_genome_overall = None
best_reward_overall = -math.inf

individual_size = ep_runner.get_individual_size()

print("Individual size: {}".format(individual_size))

if optimizer == "CMA-ES":
    opt = OptimizerCmaEs(individual_size, offspring_population_size)
elif optimizer == "Canonical-ES":
    opt = OptimizerCanonicalEs(individual_size, offspring_population_size, parent_population_size, step_size)
else:
    raise RuntimeError("No valid optimizer")

startTime = time.time()
startDate = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

log = []

# Run evolutionary training for given number of generations
for generation in range(number_generations):

    t_start = time.time()

    # Environment seed for this generation (excludes validation env seeds)
    env_seed = random.randint(number_validation_runs, maximum_env_seed)

    # Ask optimizer for new population
    genomes = opt.ask()

    # Training runs for candidates
    evaluations = []
    for genome in genomes:
        evaluations.append([genome, env_seed, number_rounds])

    rewards_training = pool.map(ep_runner.eval_fitness, evaluations)

    # Tell optimizer new rewards
    opt.tell(rewards_training)

    best_genome_current_generation = genomes[np.argmax(rewards_training)]

    # Validation runs for best individual
    evaluations = []
    for i in range(number_validation_runs):
        evaluations.append([best_genome_current_generation, i, 1])

    rewards_validation = pool.map(ep_runner.eval_fitness, evaluations)

    best_reward_current_generation = np.mean(rewards_validation)
    if best_reward_current_generation > best_reward_overall:
        best_genome_overall = best_genome_current_generation
        best_reward_overall = best_reward_current_generation

        # Save best genome
        # np.save('Best_Genome.npy', best_genome_overall)

    elapsed_time_current_generation = time.time() - t_start

    # Print info for current generation
    print("Generation: {}   "
          "Min: {:4.2f}   "
          "Mean: {:4.2f}   "
          "Max: {:4.2f}   "
          "Best: {:4.2f}   "
          "Elapsed time:  {:4.2f}s ".format(generation,
                                            np.min(rewards_training),
                                            np.mean(rewards_training),
                                            np.max(rewards_training),
                                            best_reward_overall,
                                            elapsed_time_current_generation))

    # Write current generation to log
    log_line = dict()
    log_line['gen'] = generation
    log_line['min'] = np.min(rewards_training)
    log_line['mean'] = np.mean(rewards_training)
    log_line['max'] = np.max(rewards_training)
    log_line['elapsed_time'] = elapsed_time_current_generation
    log.append(log_line)


# Create new directory to store data of current training run
directory = os.path.join('Simulation_Results', startDate)
os.makedirs(directory)

# Save best genome
np.save(os.path.join(directory, 'Best_Genome'), best_genome_overall)

# Save brain state (i.e. masks)
ep_runner.save_brain_state(os.path.join(directory, 'Brain_State'))

# Write Log to text file
with open(os.path.join(directory, 'Log.txt'), 'w') as write_file:

    write_file.write('\n')
    write_file.write('Genome Size: {:d}\n'.format(individual_size))
    # write_file.write('Inputs: {:d}\n'.format(input_size))
    # write_file.write('Outputs: {:d}\n'.format(output_size))
    write_file.write('\n')
    dash = '-' * 80
    write_file.write(dash + '\n')
    write_file.write(
        '{:<8s}{:<16s}{:<16s}{:<16s}{:<16s}\n'.format('gen', 'min', 'mean', 'max', 'elapsed time (s)'))
    write_file.write(dash + '\n')

    # Write data for each episode
    for line in log:
        write_file.write(
            '{:<8d}{:<16.2f}{:<16.2f}{:<16.2f}{:<16.2f}\n'.format(line['gen'], line['min'], line['mean'],
                                                                  line['max'], line['elapsed_time']))

    # Write elapsed time
    write_file.write("\nTime elapsed: %.4f seconds" % (time.time() - startTime))
