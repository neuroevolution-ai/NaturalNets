import json
import os
import random
import time
from datetime import datetime
import attr
import numpy as np
import math

from brains.continuous_time_rnn import ContinuousTimeRNN
from optimizer.canonical_es import OptimizerCanonicalEs
from optimizer.cma_es_deap import OptimizerCmaEsDeap
from tools.episode_runner_autoencoder import EpisodeRunnerAutoEncoder
from tools.write_results import write_results_to_textfile


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class TrainingCfg:
    environment: dict
    number_generations: int
    number_validation_runs: int
    number_rounds: int
    maximum_env_seed: int
    brain: dict
    optimizer: dict


# TODO: Do this registration via class decorators
registered_optimizer_classes = {'CMA-ES-Deap': OptimizerCmaEsDeap, 'Canonical-ES': OptimizerCanonicalEs}
registered_brain_classes = {'CTRNN': ContinuousTimeRNN}

# Load configuration file
with open("configurations/CMA_ES_Deap_CTRNN_Sparse_AutoEncoder.json", "r") as read_file:
    configuration = json.load(read_file)

config = TrainingCfg(**configuration)

# Get brain class from configuration
if config.brain['type'] in registered_brain_classes:
    brain_class = registered_brain_classes[config.brain['type']]
else:
    raise RuntimeError("No valid brain")

# Initialize episode runner
ep_runner = EpisodeRunnerAutoEncoder(environment=config.environment, brain_class=brain_class,
                                     brain_configuration=config.brain, use_gpu=True)

individual_size = ep_runner.get_individual_size()

print("Free parameters: " + str(ep_runner.get_free_parameter_usage()))
print("Individual size: {}".format(individual_size))

# Get optimizer from configuration
if config.optimizer['type'] in registered_optimizer_classes:
    optimizer_class = registered_optimizer_classes[config.optimizer['type']]
    opt = optimizer_class(individual_size=individual_size, configuration=config.optimizer)
else:
    raise RuntimeError("No valid optimizer")

best_genome_overall = None
best_reward_overall = -math.inf

start_time_training = time.time()
start_date_training = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

log = []

print("Starting main thread on PID: {}".format(os.getpid()))

# Run evolutionary training for given number of generations
for generation in range(config.number_generations):

    start_time_current_generation = time.time()

    # Environment seed for this generation (excludes validation environment seeds)
    env_seed = random.randint(config.number_validation_runs, config.maximum_env_seed)

    # Ask optimizer for new population
    genomes = opt.ask()

    # Training runs for candidates
    evaluations = []
    for genome in genomes:
        evaluations.append([genome, env_seed, config.number_rounds])

    # rewards_training = pool.map(ep_runner.eval_fitness, evaluations)
    # rewards_training = map(ep_runner.eval_fitness, evaluations)
    episode_steps: int = config.environment["episode_steps"]
    break_all_episodes: bool = config.environment["break_all_episodes"]

    rewards_training, times_episodes = ep_runner.eval_fitness(evaluations, episode_steps=episode_steps,
                                                              break_all_episodes=break_all_episodes)

    # Tell optimizer new rewards
    opt.tell(rewards_training)

    best_genome_current_generation = genomes[np.argmax(rewards_training)]

    # Validation runs for best individual
    evaluations = []
    for i in range(config.number_validation_runs):
        evaluations.append([best_genome_current_generation, i, 1])

    rewards_validation, _ = ep_runner.eval_fitness(evaluations, episode_steps=episode_steps,
                                                   break_all_episodes=break_all_episodes)

    best_reward_current_generation = np.mean(rewards_validation)
    if best_reward_current_generation > best_reward_overall:
        best_genome_overall = best_genome_current_generation
        best_reward_overall = best_reward_current_generation

    elapsed_time_current_generation = time.time() - start_time_current_generation

    # Print info for current generation
    print("Generation: {}   "
          "Min: {:4.2f}   "
          "Mean: {:4.2f}   "
          "Max: {:4.2f}   "
          "Best: {:4.2f}   "
          "Elapsed time:  {:4.2f}s "
          "Mean time per episode: {:4.2f}s".format(generation,
                                                   np.min(rewards_training),
                                                   np.mean(rewards_training),
                                                   np.max(rewards_training),
                                                   best_reward_overall,
                                                   elapsed_time_current_generation,
                                                   np.mean(times_episodes)))

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
print("Output directory: " + str(results_directory))

# Save configuration
with open(os.path.join(results_directory, 'Configuration.json'), 'w') as outfile:
    json.dump(configuration, outfile, ensure_ascii=False, indent=4)

# Save best genome
np.save(os.path.join(results_directory, 'Best_Genome'), best_genome_overall)

# Save brain state (i.e. masks)
ep_runner.save_brain_state(os.path.join(results_directory, 'Brain_State'))

# Write results to text file
write_results_to_textfile(path=os.path.join(results_directory, 'Log.txt'),
                          configuration=configuration,
                          log=log,
                          input_size=ep_runner.get_input_size(),
                          output_size=ep_runner.get_output_size(),
                          individual_size=individual_size,
                          free_parameter_usage=ep_runner.get_free_parameter_usage(),
                          elapsed_time=time.time() - start_time_training)

print("Finished")
