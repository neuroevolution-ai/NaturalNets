import json
import os
import time

import click
import numpy as np

from monkey_tester.monkey_tester import MonkeyTesterCfg, RandomMonkeyTester
from naturalnets.brains.i_brain import get_brain_class
from naturalnets.enhancers.i_enhancer import get_enhancer_class, DummyEnhancer
from naturalnets.environments.i_environment import get_environment_class


def monkey_tester_visualization(monkey_dir: str, lag: float):

    with open(os.path.join(monkey_dir, "monkey_tester_options.json"), "r") as f:
        monkey_tester_config = MonkeyTesterCfg(**json.load(f))

    with open(os.path.join(monkey_dir, "monkey_tester_details.json"), "r") as f:
        monkey_tester_details = json.load(f)

    monkey_seed = monkey_tester_details["monkey_random_seed"]

    env_config = monkey_tester_config.environment
    env_id = env_config["type"]
    env = get_environment_class(env_id)(env_config)
    env.reset(env_seed=monkey_seed)

    monkey_tester = RandomMonkeyTester(random_seed=monkey_seed, action_size=env.get_number_outputs())

    total_reward = 0
    done = False

    while not done:
        action = monkey_tester.step()

        _, reward, done, _ = env.step(action)
        total_reward += reward

        env.render()
        time.sleep(lag)

    print(f"Monkey Tester Seed {monkey_seed}: Reward {total_reward}")


def experiment_visualization(exp_dir: str, lag: float):
    # Load configuration file
    with open(os.path.join(exp_dir, "Configuration.json"), "r") as read_file:
        configuration = json.load(read_file)

    individual = np.load(os.path.join(exp_dir, "Best_Genome.npy"), allow_pickle=True)

    environment_class = get_environment_class(configuration["environment"]["type"])
    env = environment_class(configuration=configuration["environment"])

    if configuration["enhancer"]["type"] is None:
        enhancer_class = DummyEnhancer
    else:
        enhancer_class = get_enhancer_class(configuration["enhancer"]["type"])

    enhancer = enhancer_class(env.get_number_outputs())

    brain_class = get_brain_class(configuration["brain"]["type"])
    brain_state = brain_class.load_brain_state(os.path.join(exp_dir, "Brain_State.npz"))

    brain = brain_class(input_size=env.get_number_inputs(),
                        output_size=env.get_number_outputs() + enhancer.get_number_outputs(),
                        individual=individual,
                        configuration=configuration["brain"],
                        brain_state=brain_state)

    number_validation_runs = configuration["number_validation_runs"]

    fitness_total = 0

    for env_seed in range(number_validation_runs):

        env = environment_class(configuration=configuration["environment"])

        ob = env.reset()
        brain.reset()

        fitness_current = 0
        done = False

        while not done:
            action = brain.step(ob)
            action, enhancer_info = enhancer.step(action)
            ob, rew, done, info = env.step(action)
            fitness_current += rew

            env.render(enhancer_info)
            time.sleep(lag)

        fitness_total += fitness_current

        print("Seed: {}   Reward:  {:4.2f}".format(env_seed, fitness_current))

    print("Reward mean: {:4.2f}".format(fitness_total / number_validation_runs))
    print("Finished")


@click.command()
@click.option("-d", "--directory", type=str, required=True,
              help="Path to the directory of a trained experiment, or a monkey tester")
@click.option("-l", "--lag", type=float, default=0.005, show_default=True, help="Amount of seconds the script sleeps, "
                                                                                "after each step. Useful to slow down "
                                                                                "the rendering.")
def main(directory: str, lag: float):
    # Differentiate if a monkey tester or a trained experiment shall be visualized
    if os.path.exists(os.path.join(directory, "monkey_tester_options.json")):
        # directory points to a monkey tester
        monkey_tester_visualization(monkey_dir=directory, lag=lag)
    else:
        experiment_visualization(exp_dir=directory, lag=lag)


if __name__ == "__main__":
    main()
