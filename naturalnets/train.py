import json
import math
import multiprocessing
import os
import random
import time
from datetime import datetime
from typing import Optional, Dict, Union

import attrs
import numpy as np
from cpuinfo import get_cpu_info
from tensorboardX import SummaryWriter
import wandb

from naturalnets.brains.i_brain import get_brain_class
from naturalnets.enhancers.i_enhancer import get_enhancer_class, DummyEnhancer
from naturalnets.environments.i_environment import get_environment_class
from naturalnets.optimizers.i_optimizer import get_optimizer_class
from naturalnets.optimizers import DummyOptimizer
from naturalnets.tools.episode_runner import EpisodeRunner
from naturalnets.tools.utils import flatten_dict
from naturalnets.tools.write_results import write_results_to_textfile


@attrs.define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class TrainingCfg:
    number_generations: int
    number_validation_runs: int
    number_rounds: int
    maximum_env_seed: int
    fixed_env_seed: int = -1
    environment: dict
    brain: dict
    optimizer: dict
    enhancer: dict = None
    experiment_id: int = -1


def train(configuration: Optional[Union[str, Dict]] = None, results_directory: str = "results", debug: bool = False,
          w_and_b_log: bool = True):
    start_time_training = time.time()
    start_date_training = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    pool = multiprocessing.Pool()

    if w_and_b_log:
        # Use the local folder name, where the results are stored as the WandB experiment name, to match them
        # later
        wandb.init(
            entity="neuroevolution",
            project="NaturalNets",
            name=start_date_training,
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

    if individual_size == 0:
        opt = DummyOptimizer(configuration=config.optimizer)
    else:
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

        best_reward_current_generation = np.mean(rewards_validation)
        if best_reward_current_generation > best_reward_overall:
            best_genome_overall = best_genome_current_generation
            best_reward_overall = best_reward_current_generation

        elapsed_time_current_generation = time.time() - start_time_current_generation

        min_reward_training = np.min(rewards_training)
        mean_reward_training = np.mean(rewards_training)
        max_reward_training = np.max(rewards_training)

        # Print info for current generation
        print("Generation: {}   "
              "Min: {:4.2f}   "
              "Mean: {:4.2f}   "
              "Max: {:4.2f}   "
              "Best: {:4.2f}   "
              "Elapsed time:  {:4.2f}s ".format(generation,
                                                min_reward_training,
                                                mean_reward_training,
                                                max_reward_training,
                                                best_reward_overall,
                                                elapsed_time_current_generation))

        # Write current generation to log
        log_line = dict()
        log_line["gen"] = generation
        log_line["min"] = min_reward_training
        log_line["mean"] = mean_reward_training
        log_line["max"] = max_reward_training
        log_line["best"] = best_reward_overall
        log_line["elapsed_time"] = elapsed_time_current_generation
        log.append(log_line)

        wandb.log({
            "gen": generation,
            "min": min_reward_training,
            "mean": mean_reward_training,
            "max": max_reward_training,
            "best": best_reward_overall
        })

    elapsed_time = time.time() - start_time_training

    print("Elapsed time for training: %.2f seconds" % elapsed_time)

    # Create new directory to store data of current training run
    results_subdirectory = os.path.join(results_directory, start_date_training)
    os.makedirs(results_subdirectory)
    print("Output directory: " + str(results_subdirectory))

    # Save configuration
    with open(os.path.join(results_subdirectory, "Configuration.json"), "w") as outfile:
        json.dump(dict(configuration), outfile, ensure_ascii=False, indent=4)

    # Save best genome
    np.save(os.path.join(results_subdirectory, "Best_Genome"), best_genome_overall)

    # Save brain state (i.e. masks)
    ep_runner.save_brain_state(os.path.join(results_subdirectory, "Brain_State"))

    # Last element of log contains additional for training
    log_info = dict()
    log_info["elapsed_time_training"] = elapsed_time
    log_info["cpu"] = get_cpu_info()["brand_raw"]
    log.append(log_info)

    # Write log to JSON for better parsing
    with open(os.path.join(results_subdirectory, "Log.json"), "w") as outfile:
        json.dump(log, outfile, ensure_ascii=False, indent=4)

    # Write results to text file for better readability
    write_results_to_textfile(path=os.path.join(results_subdirectory, "Log.txt"),
                              configuration=configuration,
                              log=log,
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
            "hparam/max_avg": max([x["mean"] for x in log]),
            "hparam/max": max([x["max"] for x in log]),
            "hparam/best": max([x["best"] for x in log]),
        }
    )

    for log_entry in log:
        writer.add_scalar("gen", log_entry["gen"], global_step=log_entry["gen"])
        writer.add_scalar("min", log_entry["min"], global_step=log_entry["gen"])
        writer.add_scalar("mean", log_entry["mean"], global_step=log_entry["gen"])
        writer.add_scalar("max", log_entry["max"], global_step=log_entry["gen"])
        writer.add_scalar("best", log_entry["best"], global_step=log_entry["gen"])

    writer.close()

    # If there were any error messages inside the subprocesses, they are shown once
    # they are joined
    pool.close()
    pool.join()

    wandb.finish()


def initialize_sweep():
    sweep_configuration = {
        "method": "random",
        "name": "sweep",
        "metric": {
            "goal": "maximize",
            "name": "best"
        },
        "parameters": {
            "experiment_id": {"value": 7},
            "number_generations": {"value": 10},
            "number_validation_runs": {"value": 1},
            "number_rounds": {"value": 1},
            "maximum_env_seed": {"value": 100000},
            "environment": {
                "parameters": {
                    "type": {"value": "GUIApp"},
                    "number_time_steps": {"value": 100},
                    "include_fake_bug": {"value": False}
                }
            },
            # "brain": {
            #     "parameters": {
            #         "type": {"value": "CTRNN"},
            #         "delta_t": {"value": 0.05},
            #         "number_neurons": {"values": [5, 10, 20]},
            #         "differential_equation": {"value": "NaturalNet"},
            #         "v_mask": {"value": "dense"},
            #         "w_mask": {"value": "dense"},
            #         "t_mask": {"value": "dense"},
            #         "clipping_range": {"values": [1.0, 3.0]},
            #         "set_principle_diagonal_elements_of_W_negative": {"values": [False, True]},
            #         "optimize_x0": {"value": True},
            #         "alpha": {"value": 0.0}
            #     }
            # },
            "brain": {
                "parameters": {
                    "type": {"value": "RNN"},
                    "hidden_layers": {"values": [[5], [10]]},
                    "use_bias": {"values": [False, True]}
                }
            },
            "optimizer": {
                "parameters": {
                    "type": {"value": "CmaEsDeap"},
                    "population_size": {"value": 10},
                    "sigma": {"values": [0.5, 1.0, 2.0]}
                }
            },
            "enhancer": {
                "parameters": {
                    "type": {"values": [None, "RandomEnhancer"]}
                }
            }
        }
    }

    sweep_id = wandb.sweep(sweep=sweep_configuration, project="natural-nets-test")

    print(f"Initialized sweep with id: {sweep_id}")


if __name__ == "__main__":
    train()
    # initialize_sweep()
    # wandb.agent(sweep_id="deubelp/natural-nets-test/b1810zcv", function=train, count=1)
