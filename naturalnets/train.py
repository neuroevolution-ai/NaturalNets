import json
import math
import multiprocessing
import os
import random
import time
from datetime import datetime
from socket import gethostname
from typing import Optional, Dict, Union, Tuple

import click
import numpy as np
import wandb
from attrs import define, field, validators
from cpuinfo import get_cpu_info
from tensorboardX import SummaryWriter

from naturalnets.brains.i_brain import get_brain_class
from naturalnets.enhancers.i_enhancer import get_enhancer_class, DummyEnhancer
from naturalnets.environments.i_environment import get_environment_class
from naturalnets.optimizers.i_optimizer import get_optimizer_class
from naturalnets.tools.episode_runner import EpisodeRunner
from naturalnets.tools.utils import flatten_dict, set_seeds
from naturalnets.tools.write_results import write_results_to_textfile

GEN_KEY = "gen"
MIN_TRAIN_KEY = "min_train"
MEAN_TRAIN_KEY = "mean_train"
MAX_TRAIN_KEY = "max_train"
MIN_VAL_KEY = "min_val"
MEAN_VAL_KEY = "mean_val"
MAX_VAL_KEY = "max_val"
BEST_KEY = "best"
ELAPSED_KEY = "elapsed_time"


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class TrainingCfg:
    number_generations: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    number_rounds: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    number_validation_runs: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    maximum_env_seed: int = field(validator=[validators.instance_of(int), validators.ge(0)])
    fixed_env_seed: int = field(default=-1, validator=[validators.instance_of(int), validators.ge(-1)])
    environment: dict
    brain: dict
    optimizer: dict
    enhancer: dict
    experiment_id: int = field(default=-1, validator=[validators.instance_of(int), validators.ge(-1)])
    global_seed: int = field(validator=[validators.instance_of(int), validators.ge(0)])


def train(configuration: Optional[Union[str, Dict]] = None, results_directory: str = "results", debug: bool = False,
          w_and_b_log: bool = True, w_and_b_entity: str = "neuroevolution-fzi", w_and_b_project: str = "NaturalNets"):
    start_time_training = time.time()
    start_date_training = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    pool = multiprocessing.Pool()

    if w_and_b_log:
        # Use the local folder name, where the results are stored as the WandB experiment name, to match them
        # later
        wandb.init(
            entity=w_and_b_entity,
            project=w_and_b_project,
            name=f"{gethostname()}/{start_date_training}",
            config=configuration
        )

        if configuration is None:
            # This case is usually called when a WandB Hyperparameter Sweep Agent calls the function.
            # It gets a configuration from the Sweep Controller and populates the wandb.config attribute
            configuration = wandb.config

    if isinstance(configuration, str):
        with open("naturalnets/configurations/temp-config.json", "r") as config_file:
            configuration = json.load(config_file)

    if configuration is None:
        raise RuntimeError("No configuration provided!")

    config = TrainingCfg(**configuration)

    # For reproducibility, set the global random seeds
    set_seeds(config.global_seed)

    # Flatten the config already here (although it is only used at the end of training), to see if an assertion will
    # be triggered
    flattened_config = flatten_dict(configuration)

    # Get environment class from configuration
    environment_class = get_environment_class(config.environment["type"])

    # Get brain class from configuration
    brain_class = get_brain_class(config.brain["type"])

    try:
        enhancer_type = config.enhancer["type"]
    except TypeError:
        raise RuntimeError("The configuration needs an 'enhancer' block.")

    if enhancer_type is not None:
        enhancer_class = get_enhancer_class(enhancer_type)
    else:
        enhancer_class = DummyEnhancer

    # Initialize episode runner
    ep_runner = EpisodeRunner(env_class=environment_class,
                              env_configuration=config.environment,
                              brain_class=brain_class,
                              brain_configuration=config.brain,
                              enhancer_class=enhancer_class)

    individual_size = ep_runner.get_individual_size()

    print("Free parameters: " + str(ep_runner.get_free_parameter_usage()))
    print("Individual size: {}".format(individual_size))
    print("Used CPU for training: " + get_cpu_info()["brand_raw"])

    # Get optimizer class from configuration
    optimizer_class = get_optimizer_class(config.optimizer["type"])

    opt = optimizer_class(individual_size=individual_size, configuration=config.optimizer)

    best_genome_overall = None
    best_reward_overall = -math.inf

    log = []

    # Run evolutionary training for given number of generations
    for generation in range(config.number_generations):

        start_time_current_generation = time.time()

        # Environment seed for this generation
        if config.fixed_env_seed == -1:
            # Excludes validation environment seeds
            env_seed = random.randint(config.number_validation_runs, config.maximum_env_seed)
        else:
            env_seed = config.fixed_env_seed

        # Ask optimizers for new population
        genomes = opt.ask()

        # Training runs for candidates
        evaluations = []
        for genome in genomes:
            evaluations.append([genome, env_seed, config.number_rounds])

        if debug:
            # Use this for debugging
            rewards_training = [ep_runner.eval_fitness(individual_eval) for individual_eval in evaluations]
        else:
            rewards_training = pool.map(ep_runner.eval_fitness, evaluations)

        # Tell optimizers new rewards
        opt.tell(rewards_training)

        best_genome_current_generation = genomes[np.argmax(rewards_training)]

        # Validation runs for best individual
        evaluations = []
        for i in range(config.number_validation_runs):
            evaluations.append([best_genome_current_generation, i, 1])

        if debug:
            rewards_validation = [ep_runner.eval_fitness(individual_eval) for individual_eval in evaluations]
        else:
            rewards_validation = pool.map(ep_runner.eval_fitness, evaluations)

        min_reward_validation = np.min(rewards_validation)
        mean_reward_validation = np.mean(rewards_validation)
        max_reward_validation = np.max(rewards_validation)

        best_reward_current_generation = mean_reward_validation
        if best_reward_current_generation > best_reward_overall:
            best_genome_overall = best_genome_current_generation
            best_reward_overall = best_reward_current_generation

        elapsed_time_current_generation = time.time() - start_time_current_generation

        min_reward_training = np.min(rewards_training)
        mean_reward_training = np.mean(rewards_training)
        max_reward_training = np.max(rewards_training)

        log_line = {
            GEN_KEY: generation,
            MIN_TRAIN_KEY: min_reward_training,
            MEAN_TRAIN_KEY: mean_reward_training,
            MAX_TRAIN_KEY: max_reward_training,
            MIN_VAL_KEY: min_reward_validation,
            MEAN_VAL_KEY: mean_reward_validation,
            MAX_VAL_KEY: max_reward_validation,
            BEST_KEY: best_reward_overall,
            ELAPSED_KEY: elapsed_time_current_generation
        }

        # Print info for current generation
        print(f"Generation: {generation}   "
              f"Min: {min_reward_training:4.2f}   "
              f"Mean: {mean_reward_training:4.2f}   "
              f"Max: {max_reward_training:4.2f}   "
              f"Min Val: {min_reward_validation:4.2f}   "
              f"Mean Val: {mean_reward_validation:4.2f}   "
              f"Max Val: {max_reward_validation:4.2f}   "
              f"Best: {best_reward_overall:4.2f}   "
              f"Elapsed time:  {elapsed_time_current_generation:4.2f}s ")

        # Append current generation to log
        log.append(log_line)

        if w_and_b_log:
            wandb.log(log_line)

    elapsed_time = time.time() - start_time_training

    print(f"Elapsed time for training: {elapsed_time:.2f} seconds")

    # Create new directory to store data of current training run
    results_subdirectory = os.path.join(results_directory, start_date_training)
    os.makedirs(results_subdirectory)
    print(f"Output directory: {results_subdirectory}")

    # Save configuration
    with open(os.path.join(results_subdirectory, "Configuration.json"), "w") as outfile:
        json.dump(dict(configuration), outfile, ensure_ascii=False, indent=4)

    # Save best genome
    np.save(os.path.join(results_subdirectory, "Best_Genome"), best_genome_overall)

    # Save brain state (i.e. masks)
    ep_runner.save_brain_state(os.path.join(results_subdirectory, "Brain_State"))

    # Last element of log contains additional for training
    log.append({
        "elapsed_time_training": elapsed_time,
        "cpu": get_cpu_info()["brand_raw"]
    })

    # Write log to JSON for better parsing
    with open(os.path.join(results_subdirectory, "Log.json"), "w") as outfile:
        json.dump(log, outfile, ensure_ascii=False, indent=4)

    # Write results to text file for better readability
    write_results_to_textfile(path=os.path.join(results_subdirectory, "Log.txt"),
                              configuration=configuration,
                              log=log,
                              log_entry_keys=[
                                  GEN_KEY,
                                  MIN_TRAIN_KEY, MEAN_TRAIN_KEY, MAX_TRAIN_KEY,
                                  MIN_VAL_KEY, MEAN_VAL_KEY, MAX_VAL_KEY,
                                  BEST_KEY, ELAPSED_KEY
                              ],
                              input_size=ep_runner.get_input_size(),
                              output_size=ep_runner.get_output_size(),
                              individual_size=individual_size,
                              free_parameter_usage=ep_runner.get_free_parameter_usage())

    print("Adding data to TensorBoard...")
    writer = SummaryWriter(
        logdir=results_subdirectory
    )

    writer.add_hparams(
        flattened_config,
        {
            "hparam/max_of_mean_train": max([x[MEAN_TRAIN_KEY] for x in log]),
            "hparam/max_train": max([x[MAX_TRAIN_KEY] for x in log]),
            "hparam/best": best_reward_overall,
        }
    )

    for log_entry in log:
        writer.add_scalar(GEN_KEY, log_entry[GEN_KEY], global_step=log_entry[GEN_KEY])
        writer.add_scalar(MIN_TRAIN_KEY, log_entry[MIN_TRAIN_KEY], global_step=log_entry[GEN_KEY])
        writer.add_scalar(MEAN_TRAIN_KEY, log_entry[MEAN_TRAIN_KEY], global_step=log_entry[GEN_KEY])
        writer.add_scalar(MAX_TRAIN_KEY, log_entry[MAX_TRAIN_KEY], global_step=log_entry[GEN_KEY])
        writer.add_scalar(MIN_VAL_KEY, log_entry[MIN_VAL_KEY], global_step=log_entry[GEN_KEY])
        writer.add_scalar(MEAN_VAL_KEY, log_entry[MEAN_VAL_KEY], global_step=log_entry[GEN_KEY])
        writer.add_scalar(MAX_VAL_KEY, log_entry[MAX_VAL_KEY], global_step=log_entry[GEN_KEY])
        writer.add_scalar(BEST_KEY, log_entry[BEST_KEY], global_step=log_entry[GEN_KEY])

    writer.close()

    # If there were any error messages inside the subprocesses, they are shown once
    # they are joined
    pool.close()
    pool.join()

    if w_and_b_log:
        wandb.finish()


@click.command()
@click.option("-s", "--sweep", type=str, multiple=True,
              help="WandB hyperparameter sweep ID. If provided, all other parameters are ignored. It is also possible "
                   "to provide multiple sweeps which are executed one after another.")
@click.option("-sc", "--sweep-count", type=int)
@click.option("-c", "--config", type=str, help="Path to a configuration for a monkey tester")
@click.option("-d", "--directory", type=str, default="results")
@click.option("--debug/--no-debug", type=bool, default=False)
@click.option("--wandb/--no-wandb", "w_and_b_log", type=bool, default=True)
@click.option("-we", "--wandb-entity", "w_and_b_entity", type=str, default="neuroevolution-fzi")
@click.option("-wp", "--wandb-project", "w_and_b_project", type=str, default="NaturalNets")
def train_cli(sweep: Tuple[str], sweep_count: int, config: str, directory: str, debug: bool,
              w_and_b_log: bool, w_and_b_entity: str, w_and_b_project: str):
    if len(sweep) > 0:
        for concrete_sweep in sweep:
            wandb.agent(sweep_id=concrete_sweep, function=train, count=sweep_count)
    else:
        train(
            configuration=config,
            results_directory=directory,
            debug=debug,
            w_and_b_log=w_and_b_log,
            w_and_b_entity=w_and_b_entity,
            w_and_b_project=w_and_b_project
        )


if __name__ == "__main__":
    train_cli()
