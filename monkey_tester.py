import json
import logging
import multiprocessing as mp
import os
import shutil
import sys
import time
from copy import deepcopy
from datetime import datetime
from typing import Tuple

import click
import numpy as np

from naturalnets.environments.i_environment import get_environment_class

RANDOM_CLICK_MONKEY_TYPE = "random-clicks"
RANDOM_WIDGET_MONKEY_TYPE = "random-widgets"


class RandomMonkeyTester:

    def __init__(self, random_seed: int, action_size: int):
        self.rng = np.random.default_rng(seed=random_seed)
        self.action_size = action_size

    def step(self):
        return self.rng.uniform(low=-1.0, high=1.0, size=self.action_size).astype(np.float32)


def _rollout_one_iteration(env, monkey, reward_sum: float, rewards: list,
                           actions: list) -> Tuple[float, list, list]:
    action = monkey.step()

    observation, reward, done, info = env.step(action)

    reward_sum += reward

    rewards += [reward]
    actions += [action]

    return reward_sum, rewards, actions


def _time_mode_rollout(amount: int, env, monkey) -> Tuple[float, list, list]:
    reward_sum = 0
    rewards = []
    actions = []

    start_time = time.time()

    while time.time() < start_time + amount:
        reward_sum, rewards, actions = _rollout_one_iteration(env, monkey, reward_sum, rewards, actions)

    return reward_sum, rewards, actions


def _iteration_mode_rollout(amount: int, env, monkey) -> Tuple[float, list, list]:
    reward_sum = 0
    rewards = []
    actions = []

    for i in range(amount):
        reward_sum, rewards, actions = _rollout_one_iteration(env, monkey, reward_sum, rewards, actions)

    return reward_sum, rewards, actions


def run_episode(env_config: dict, monkey_type: str, monkey_random_seed: int, amount: int,
                stop_mode: str) -> Tuple[float, list, list]:
    env_id = env_config["type"]
    env = get_environment_class(env_id)(env_config)
    env.reset()

    if monkey_type == RANDOM_CLICK_MONKEY_TYPE:
        monkey = RandomMonkeyTester(monkey_random_seed, env.get_number_outputs())
    else:
        raise NotImplementedError(f"Monkey type {monkey_type} not yet implemented")

    if stop_mode == "time":
        reward_sum, rewards, actions = _time_mode_rollout(amount, env, monkey)
    else:
        reward_sum, rewards, actions = _iteration_mode_rollout(amount, env, monkey)

    return reward_sum, rewards, actions


@click.command()
@click.option("-t", "--time", "stop_mode", flag_value="time", default=True, show_default=True,
              help="Use elapsed time in seconds to stop the monkey testing")
@click.option("-i", "--iterations", "stop_mode", flag_value="iterations", show_default=True,
              help="Use the number of iterations to stop the monkey testing")
@click.option("--amount", type=int, required=True,
              help="Amount on how long the monkey testing shall run (seconds or number of iterations, depending on "
                   "stop_mode")
@click.option("-m", "--monkey-type", default=RANDOM_CLICK_MONKEY_TYPE,
              type=click.Choice([RANDOM_CLICK_MONKEY_TYPE, RANDOM_WIDGET_MONKEY_TYPE]), show_default=True,
              help="Choose which type of random monkey tester to use")
@click.option("--random-click-prob", type=float, help="If the random widget monkey tester is chosen, use this to "
                                                      "define the probability for random clicks")
@click.option("-c", "--config", type=str, required=True,
              help="JSON configuration for the environment. Can be directly the config of the environment or a "
                   "configuration of a successful training run from which the environment's config is automatically "
                   "extracted. Note that the configured number of timesteps is ignored because of 'stop_mode' and "
                   "'--amount'.")
@click.option("-s", "--sequences", type=int, default=1,
              help="Defines the amount of monkey testers that shall be run. If processes > 1, they run in parallel,"
                   "otherwise they run sequentially.")
@click.option("-p", "--processes", "num_processes", type=int, default=mp.cpu_count(),
              help="The number of processes to use for the monkey testing")
@click.option("--root-dir", type=str, default="results_monkey/",
              help="In this directory, subfolders are automatically created based on the current time")
@click.option("--directory", type=str,
              help="This directory is directly used to store the result of the monkey testing, instead of"
                   "automatically generated subfolders as with '--root-dir'")
def main(stop_mode: str, amount: int, monkey_type: str, random_click_prob: float, config: str,
         sequences: int, num_processes: int, root_dir: str, directory: str):
    if directory is not None:
        main_chosen_directory = directory
    else:
        main_chosen_directory = os.path.join(root_dir, monkey_type, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    try:
        shutil.rmtree(main_chosen_directory)
    except FileNotFoundError:
        pass

    concrete_directories = [f"{main_chosen_directory}-{i}" for i in range(sequences)]

    for _dir in concrete_directories:
        # Create directories already here so that if an error is thrown it is done immediately and not after the
        # monkey testing (which could take some time)
        os.makedirs(_dir, exist_ok=False)

    logger = logging.getLogger("")
    formatter = logging.Formatter("[%(asctime)s] - %(funcName)s - %(message)s", datefmt="%a, %d %b %Y %H:%M:%S")

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)

    rng = np.random.default_rng()

    with open(config, "r") as f:
        config_data = json.load(f)

    if "environment" in config_data:
        env_config = config_data["environment"]
    else:
        # Otherwise assume config_data is already only the environment config
        env_config = config_data

    assert env_config["type"] == "DummyApp" or env_config["type"] == "GUIApp", ("Only these two environments are "
                                                                                "supported in this script")

    if "number_time_steps" in env_config and env_config["number_time_steps"] is not None:
        logging.warning("The chosen number of timesteps in the environment config are ignored. In this script,"
                        "the CLI parameter 'amount' overwrites the environment config's timesteps!")

    random_seeds = rng.integers(2**32, size=sequences)

    results = []
    with mp.Pool(num_processes) as p:
        for monkey_seed in random_seeds:
            results.append(p.apply_async(run_episode, (env_config, monkey_type, monkey_seed, amount, stop_mode)))

        results = [r.get() for r in results]

    general_monkey_tester_options = {
        "environment": {
            **env_config
        },
        "stop-mode": stop_mode,
        "amount": amount,
        "monkey-type": monkey_type,
        "random-click-probability": random_click_prob,
        "root-dir": root_dir,
        "explicit-dir": directory
    }

    for _dir, res, seed in zip(concrete_directories, results, random_seeds):
        monkey_tester_options = deepcopy(general_monkey_tester_options)
        monkey_tester_options["monkey_random_seed"] = int(seed)  # Must convert to standard Python type because of json

        reward_sum, rewards, actions = res

        current_dir = os.path.join(_dir, "data.npz")
        np.savez(
            current_dir,
            rewards=np.array(rewards, dtype=np.float32),
            actions=np.array(actions, dtype=np.float32)
        )

        logging.info(f"Finished monkey testing with a summed up reward of {reward_sum} in directory: {current_dir}")

        with open(os.path.join(_dir, "monkey_tester_options.json"), "w", encoding="utf-8") as f:
            json.dump(monkey_tester_options, f, indent=4)

    logging.info("Monkey Testing finished")


if __name__ == '__main__':
    main()
