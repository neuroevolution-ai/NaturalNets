import time
import os
from episode_runner import *
import multiprocessing
import random
from optimizer.cma_es import *
from optimizer.canonical_es import *
from tools.write_results import write_results_to_textfile
from datetime import datetime


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class ExperimentCfg:
    environment: str
    number_generations: int
    number_validation_runs: int
    number_rounds: int
    maximum_env_seed: int


pool = multiprocessing.Pool()

# Offspring population size (lambda)
#offspring_population_size = 112

# Parent population size (mu)
#parent_population_size = 50

# Mutation step size (sigma)
#step_size = 0.05


experiment_configuration = dict()
experiment_configuration['environment'] = 'procgen:procgen-heist-v0'
experiment_configuration['number_generations'] = 5
experiment_configuration['number_validation_runs'] = 100
experiment_configuration['number_rounds'] = 5
experiment_configuration['maximum_env_seed'] = 100000

brain_configuration = dict()
brain_configuration['type'] = "CTRNN"
brain_configuration['delta_t'] = 0.05
brain_configuration['number_neurons'] = 200
brain_configuration['v_mask_param'] = 0.0005
brain_configuration['w_mask_param'] = 0.05
brain_configuration['t_mask_param'] = 0.1
brain_configuration['clipping_range_min'] = -1.0
brain_configuration['clipping_range_max'] = 1.0

optimizer_configuration = dict()
optimizer_configuration['type'] = "CMA-ES"
optimizer_configuration['population_size'] = 112
optimizer_configuration['sigma'] = 1.0


config = ExperimentCfg(**experiment_configuration)

# Initialize episode runner
ep_runner = EpisodeRunner(env_name=config.environment, brain_configuration=brain_configuration)

best_genome_overall = None
best_reward_overall = -math.inf

individual_size = ep_runner.get_individual_size()

print("Individual size: {}".format(individual_size))

if optimizer_configuration['type'] == "CMA-ES":
    opt = OptimizerCmaEs(individual_size=individual_size, configuration=optimizer_configuration)
#elif optimizer_configuration['type'] == "Canonical-ES":
#    opt = OptimizerCanonicalEs(individual_size, offspring_population_size, parent_population_size, step_size)
else:
    raise RuntimeError("No valid optimizer")

start_time_training = time.time()
start_date_training = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

log = []

# Run evolutionary training for given number of generations
for generation in range(config.number_generations):

    start_time_current_generation = time.time()

    # Environment seed for this generation (excludes validation env seeds)
    env_seed = random.randint(config.number_validation_runs, config.maximum_env_seed)

    # Ask optimizer for new population
    genomes = opt.ask()

    # Training runs for candidates
    evaluations = []
    for genome in genomes:
        evaluations.append([genome, env_seed, config.number_rounds])

    rewards_training = pool.map(ep_runner.eval_fitness, evaluations)

    # Tell optimizer new rewards
    opt.tell(rewards_training)

    best_genome_current_generation = genomes[np.argmax(rewards_training)]

    # Validation runs for best individual
    evaluations = []
    for i in range(config.number_validation_runs):
        evaluations.append([best_genome_current_generation, i, 1])

    rewards_validation = pool.map(ep_runner.eval_fitness, evaluations)

    best_reward_current_generation = np.mean(rewards_validation)
    if best_reward_current_generation > best_reward_overall:
        best_genome_overall = best_genome_current_generation
        best_reward_overall = best_reward_current_generation

        # Save best genome
        # np.save('Best_Genome.npy', best_genome_overall)

    elapsed_time_current_generation = time.time() - start_time_current_generation

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

print("Elapsed time for training: %.2f seconds" % (time.time() - start_time_training))

# Create new directory to store data of current training run
results_directory = os.path.join('Simulation_Results', start_date_training)
os.makedirs(results_directory)

# Save best genome
np.save(os.path.join(results_directory, 'Best_Genome'), best_genome_overall)

# Save brain state (i.e. masks)
ep_runner.save_brain_state(os.path.join(results_directory, 'Brain_State'))

# Write Results to text file
write_results_to_textfile(path=os.path.join(results_directory, 'Log.txt'), log=log, individual_size=individual_size,
                          elapsed_time=time.time() - start_time_training)

print("Finished")
