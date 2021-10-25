import json
import math
import multiprocessing
import os
import random
import time
from datetime import datetime
from cpuinfo import get_cpu_info

import attr
import numpy as np

from naturalnets.brains.i_brain import get_brain_class
from naturalnets.environments.i_environment import get_environment_class
from naturalnets.optimizers.i_optimizer import get_optimizer_class
from naturalnets.tools.episode_runner import EpisodeRunner
from naturalnets.tools.write_results import write_results_to_textfile


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class TrainingCfg:
    number_generations: int
    number_validation_runs: int
    number_rounds: int
    maximum_env_seed: int
    environment: dict
    brain: dict
    optimizer: dict
    experiment_id: int = -1


def train(configuration, results_directory):

    pool = multiprocessing.Pool()

    config = TrainingCfg(**configuration)

    # Get environment class from configuration
    environment_class = get_environment_class(config.environment['type'])

    # Get brain class from configuration
    brain_class = get_brain_class(config.brain['type'])

    # Initialize episode runner
    ep_runner = EpisodeRunner(env_class=environment_class,
                              env_configuration=config.environment,
                              brain_class=brain_class,
                              brain_configuration=config.brain)

    individual_size = ep_runner.get_individual_size()

    print("Free parameters: " + str(ep_runner.get_free_parameter_usage()))
    print("Individual size: {}".format(individual_size))
    print("Used CPU for training: " + get_cpu_info()["brand_raw"])

    # Get optimizer class from configuration
    optimizer_class = get_optimizer_class(config.optimizer['type'])

    opt = optimizer_class(individual_size=individual_size, configuration=config.optimizer)

    best_genome_overall = None
    best_reward_overall = -math.inf

    start_time_training = time.time()
    start_date_training = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    log = []

    # Run evolutionary training for given number of generations
    for generation in range(config.number_generations):

        start_time_current_generation = time.time()

        # Environment seed for this generation (excludes validation environment seeds)
        env_seed = random.randint(config.number_validation_runs, config.maximum_env_seed)

        # Ask optimizers for new population
        genomes = opt.ask()

        # Training runs for candidates
        evaluations = []
        for genome in genomes:
            evaluations.append([genome, env_seed, config.number_rounds])

        rewards_training = pool.map(ep_runner.eval_fitness, evaluations)

        # Use this for debugging
        # rewards_training = [ep_runner.eval_fitness(individual_eval) for individual_eval in evaluations]

        # Tell optimizers new rewards
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
        log_line['best'] = best_reward_overall
        log_line['elapsed_time'] = elapsed_time_current_generation
        log.append(log_line)

    elapsed_time = time.time() - start_time_training

    print("Elapsed time for training: %.2f seconds" % elapsed_time)

    # Create new directory to store data of current training run
    results_subdirectory = os.path.join(results_directory, start_date_training)
    os.makedirs(results_subdirectory)
    print("Output directory: " + str(results_subdirectory))

    # Save configuration
    with open(os.path.join(results_subdirectory, 'Configuration.json'), 'w') as outfile:
        json.dump(configuration, outfile, ensure_ascii=False, indent=4)

    # Save best genome
    np.save(os.path.join(results_subdirectory, 'Best_Genome'), best_genome_overall)

    # Save brain state (i.e. masks)
    ep_runner.save_brain_state(os.path.join(results_subdirectory, 'Brain_State'))

    # Last element of log contains additional for training
    log_info = dict()
    log_info["elapsed_time_training"] = elapsed_time
    log_info["cpu"] = get_cpu_info()["brand_raw"]
    log.append(log_info)

    # Write log to JSON for better parsing
    with open(os.path.join(results_subdirectory, 'Log.json'), 'w') as outfile:
        json.dump(log, outfile, ensure_ascii=False, indent=4)
        
    # Write results to text file for better readibility
    write_results_to_textfile(path=os.path.join(results_subdirectory, 'Log.txt'),
                              configuration=configuration,
                              log=log,
                              input_size=ep_runner.get_input_size(),
                              output_size=ep_runner.get_output_size(),
                              individual_size=individual_size,
                              free_parameter_usage=ep_runner.get_free_parameter_usage())

    # Error messages inside subprocesses could be shown once they are joined
    pool.close()
    pool.join()
