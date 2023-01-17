import json
import logging
import multiprocessing as mp
import os
import sys
import time
from copy import deepcopy
from datetime import datetime
from functools import partial
from typing import List, Union

import click
import h5py
import numpy as np
from attrs import asdict, define, field, validators

from naturalnets.environments.i_environment import get_environment_class

RANDOM_CLICK_MONKEY_TYPE = "random-clicks"
RANDOM_WIDGET_MONKEY_TYPE = "random-widgets"


def check_categorical(possible_arguments: List[str], instance, attribute, value):
    if value not in possible_arguments:
        raise ValueError(f"'{attribute.name}' must be one of the following values: {*possible_arguments,}, and not "
                         f"'{value}'")


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class MonkeyTesterCfg:
    # Number of monkey testers to start. Must be lower than 200.000 because this is the limit for rows in a WandB.Table
    num_monkeys: int = field(validator=[validators.instance_of(int), validators.gt(0)])

    # Number of processes to use, for parallel execution. Omitting this parameter will use all available
    # threads of that processor
    num_processes: int = field(default=mp.cpu_count(), validator=[validators.instance_of(int), validators.gt(0)])

    # Currently only `"random-clicks"` supported, which simply clicks randomly at each step
    monkey_tester_type: str = field(validator=[
        validators.instance_of(str),
        partial(check_categorical, [RANDOM_CLICK_MONKEY_TYPE, RANDOM_WIDGET_MONKEY_TYPE])]
    )

    # For future use, if the random-widgets type monkey tester is used, decide the percentage of clicks that shall be
    # completely random
    random_click_prob: float = field(
        default=None,
        validator=validators.optional([validators.instance_of(float), validators.ge(0)])
    )

    # Configuration of an environment, like in a normal training experiment
    environment: dict

    # Where to store the monkey tester results
    results_dir: str = field(default="results_monkey/", validator=validators.instance_of(str))

    # Whether to store the chosen actions and rewards in a zipped NumPy archive. Should not be necessary, because the
    # monkey testers are seeded and therefore always produce the same results
    store_individual_monkey_data: bool = field(default=False, validator=validators.instance_of(bool))


class RandomMonkeyTester:

    def __init__(self, random_seed: int, action_size: int):
        self.rng = np.random.default_rng(seed=random_seed)
        self.action_size = action_size

    def step(self):
        return self.rng.uniform(low=-1.0, high=1.0, size=self.action_size).astype(np.float32)


def _save_monkey_tester_results(configuration: MonkeyTesterCfg, directory: str, monkey_random_seed: int,
                                time_started: str, time_ended: str, rewards: List, actions: List, reward_sum):
    os.makedirs(directory, exist_ok=False)

    monkey_tester_options = deepcopy(asdict(configuration))
    monkey_tester_options["monkey_random_seed"] = monkey_random_seed

    monkey_tester_options["time_started"] = time_started
    monkey_tester_options["time_ended"] = time_ended

    np.savez(
        os.path.join(directory, "data.npz"),
        rewards=np.array(rewards, dtype=np.float32),
        actions=np.array(actions, dtype=np.float32)
    )

    with open(os.path.join(directory, "monkey_tester_options.json"), "w", encoding="utf-8") as f:
        json.dump(asdict(configuration), f, indent=4)

    with open(os.path.join(directory, "monkey_tester_details.json"), "w", encoding="utf-8") as f:
        monkey_tester_details = {
            "reward_sum": reward_sum,
            "monkey_random_seed": monkey_random_seed,
            "time_started": time_started,
            "time_ended": time_ended
        }

        json.dump(monkey_tester_details, f, indent=4)


def run_episode(configuration: MonkeyTesterCfg, directory: str, monkey_random_seed: int):
    time_started = datetime.fromtimestamp(time.time()).strftime("%a, %d %b %Y %H:%M:%S")

    env_config = configuration.environment
    env_id = env_config["type"]
    env = get_environment_class(env_id)(env_config)
    env.reset(env_seed=monkey_random_seed)

    if configuration.monkey_tester_type == RANDOM_CLICK_MONKEY_TYPE:
        monkey = RandomMonkeyTester(monkey_random_seed, env.get_number_outputs())
    else:
        raise NotImplementedError(f"Monkey type {configuration.monkey_tester_type} not yet implemented")

    reward_sum = 0
    rewards = []
    actions = []

    done = False

    while not done:
        action = monkey.step()

        observation, reward, done, info = env.step(action)

        reward_sum += reward
        rewards += [reward]
        actions += [action]

    time_ended = datetime.fromtimestamp(time.time()).strftime("%a, %d %b %Y %H:%M:%S")

    log_msg = f"Monkey Tester finished: Reward {reward_sum} - Started {time_started} - Ended {time_ended}"

    if configuration.store_individual_monkey_data:
        log_msg += f" - Directory {directory}"

        _save_monkey_tester_results(
            configuration=configuration,
            directory=directory,
            monkey_random_seed=monkey_random_seed,
            time_started=time_started,
            time_ended=time_ended,
            rewards=rewards,
            actions=actions,
            reward_sum=reward_sum
        )

    logging.info(log_msg)

    return reward_sum


@click.command()
@click.option("-c", "--config", type=str, help="Path to a configuration for a monkey tester")
def main(config: Union[str, dict]):
    logger = logging.getLogger("")
    formatter = logging.Formatter("[%(asctime)s] - %(funcName)s - %(message)s", datefmt="%a, %d %b %Y %H:%M:%S")

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)

    if isinstance(config, str):
        with open(config, "r") as f:
            configuration = MonkeyTesterCfg(**json.load(f))
    else:
        configuration = MonkeyTesterCfg(**config)

    main_chosen_directory = os.path.join(
        configuration.results_dir,
        configuration.monkey_tester_type,
        datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    )

    os.makedirs(main_chosen_directory)

    concrete_directories = [
        os.path.join(main_chosen_directory, f"monkey-{i}") for i in range(configuration.num_monkeys)
    ]

    if configuration.store_individual_monkey_data:
        for _dir in concrete_directories:
            # Test if any directory already exists and raise an error if that is the case. We do not want
            # to overwrite existing results.
            if os.path.exists(_dir):
                raise RuntimeError(f"'{_dir}' already exists, please choose another directory")

    # Do not seed this, as we want always different seeds for the monkey tester. This RNG is only used to randomly
    # generate seeds for the monkey tester, that we can save in the config to reproduce later
    rng = np.random.default_rng()

    random_seeds = rng.choice(2**32, size=configuration.num_monkeys, replace=False)

    results = []
    with mp.Pool(configuration.num_processes) as p:
        for i, (_dir, monkey_seed) in enumerate(zip(concrete_directories, random_seeds)):
            results.append((i, int(monkey_seed), p.apply_async(run_episode, (configuration, _dir, int(monkey_seed)))))

        # Wait for all processes to finish by getting the results from the processes
        monkey_rewards = [[i, seed, r.get()] for i, seed, r in results]
        assert len(monkey_rewards) == configuration.num_monkeys

        with h5py.File(os.path.join(main_chosen_directory, f"monkey-rewards.hdf5"), "w") as f:
            f.create_dataset("monkey_rewards", data=monkey_rewards)

    logging.info("Monkey Testing finished")


if __name__ == '__main__':
    main()
