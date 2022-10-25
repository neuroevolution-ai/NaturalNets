import json
import logging
import multiprocessing as mp
import os
import sys
import time
from copy import deepcopy
from datetime import datetime
from functools import partial
from socket import gethostname
from typing import List, Union

import click
import numpy as np
import wandb
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
    num_monkeys: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    num_processes: int = field(default=mp.cpu_count(), validator=[validators.instance_of(int), validators.gt(0)])

    monkey_tester_type: str = field(validator=[
        validators.instance_of(str),
        partial(check_categorical, [RANDOM_CLICK_MONKEY_TYPE, RANDOM_WIDGET_MONKEY_TYPE])]
    )
    random_click_prob: float = field(
        default=None,
        validator=validators.optional([validators.instance_of(float), validators.ge(0)])
    )

    environment: dict

    results_dir: str = field(default="results_monkey/", validator=validators.instance_of(str))
    store_monkey_tester_data: bool = field(default=False, validator=validators.instance_of(bool))

    wandb_logging: bool = field(default=True, validator=validators.instance_of(bool))
    wandb_entity: str = field(default="neuroevolution", validator=validators.instance_of(str))
    wandb_project: str = field(default="NaturalNets", validator=validators.instance_of(str))


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

    if configuration.store_monkey_tester_data:
        np.savez(
            os.path.join(directory, "data.npz"),
            rewards=np.array(rewards, dtype=np.float32),
            actions=np.array(actions, dtype=np.float32)
        )

    logging.info(f"Monkey Tester finished: Reward {reward_sum} - Started {time_started} - Ended {time_ended} - "
                 f"Directory {directory}")

    with open(os.path.join(directory, "monkey_tester_options.json"), "w", encoding="utf-8") as f:
        json.dump(monkey_tester_options, f, indent=4)


def run_episode(configuration: MonkeyTesterCfg, directory: str, monkey_random_seed: int):

    if configuration.wandb_logging:
        wandb.init(
            entity=configuration.wandb_entity,
            project=configuration.wandb_project,
            name=f"{gethostname()}/{configuration.monkey_tester_type}/{os.path.basename(directory)}",
            config=asdict(configuration),
            tags=["monkey"]
        )

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

        if configuration.wandb_logging:
            wandb.log({
                "rew": reward_sum
            })

    time_ended = datetime.fromtimestamp(time.time()).strftime("%a, %d %b %Y %H:%M:%S")

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

    if configuration.wandb_logging:
        wandb.finish()


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

    concrete_directories = [f"{main_chosen_directory}-{i}" for i in range(configuration.num_monkeys)]

    for _dir in concrete_directories:
        # Test if any directory already exists and raise an error if that is the case. We do not want
        # to overwrite existing results.
        if os.path.exists(_dir):
            raise RuntimeError(f"'{_dir}' already exists, please choose another directory")

    # Do not seed this, as we want always different seeds for the monkey tester. This RNG is only used to randomly
    # generate seeds for the monkey tester, that we can save in the config to reproduce later
    rng = np.random.default_rng()

    random_seeds = rng.integers(2**32, size=configuration.num_monkeys)

    results = []
    with mp.Pool(configuration.num_processes) as p:
        for _dir, monkey_seed in zip(concrete_directories, random_seeds):
            results.append(p.apply_async(run_episode, (configuration, _dir, int(monkey_seed))))

        # Wait for all processes to finish
        [r.wait() for r in results]

    logging.info("Monkey Testing finished")


if __name__ == '__main__':
    main()
