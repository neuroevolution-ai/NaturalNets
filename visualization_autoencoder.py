import json
import os
import time

import attr
import gym3
import numpy as np
from procgen import ProcgenGym3Env

from brains.continuous_time_rnn import ContinuousTimeRNN
from tools.episode_runner_autoencoder import EpisodeRunnerAutoEncoder


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class TrainingCfg:
    environment: dict
    number_generations: int
    number_validation_runs: int
    number_rounds: int
    maximum_env_seed: int
    brain: dict
    optimizer: dict


directory = os.path.join('Simulation_Results', '2021-03-20_00-38-46')

# Load configuration file
with open(os.path.join(directory, 'Configuration.json'), "r") as read_file:
    configuration = json.load(read_file)

config = TrainingCfg(**configuration)

brain_state = ContinuousTimeRNN.load_brain_state(os.path.join(directory, 'Brain_State.npz'))

individual = np.load(os.path.join(directory, 'Best_Genome.npy'), allow_pickle=True)

brain = ContinuousTimeRNN(input_size=0, output_size=0, individual=individual, configuration=config.brain,
                          brain_state=brain_state)

ep_runner = EpisodeRunnerAutoEncoder(environment=config.environment, brain_class=ContinuousTimeRNN,
                                     brain_configuration=config.brain, use_gpu=True)

env_name = config.environment["name"]
# Convert env name to gym3 compatible env name
if env_name == "procgen:procgen-heist-v0":
    env_name = "heist"

distribution_mode = config.environment["distribution_mode"]
episode_steps = config.environment["episode_steps"]

reward_sum = 0
number_validation_runs = 100

num_levels_solved = 0

for env_seed in range(number_validation_runs):

    env = ProcgenGym3Env(num=1, env_name=env_name, use_backgrounds=False, distribution_mode=distribution_mode,
                         num_levels=1, start_level=env_seed, render_mode="rgb_array")
    env = gym3.ViewerWrapper(env, info_key="rgb")

    _, ob, _ = env.observe()
    observations = ob["rgb"]
    ob = ep_runner.transform_ob(observations)

    reward = 0

    brain.reset()

    for i in range(episode_steps):
        action = brain.step(ob.flatten())
        action = np.array([np.argmax(action)])
        env.act(action)
        rew, ob, first = env.observe()

        reward += rew[0]

        if any(first):
            break

        observations = ob["rgb"]
        ob = ep_runner.transform_ob(observations)

        # obs = cv2.resize(ob, (20, 20), interpolation=cv2.INTER_AREA)

        # cv2.imshow("ProcGen Agent", cv2.resize(ob, (500, 500)))
        # cv2.waitKey(1)

        # time.sleep(0.01)

    reward_sum += reward

    env._renderer.finish()

    if reward > 0:
        num_levels_solved += 1

    print("Seed: {}   Reward:  {:4.2f}".format(env_seed, reward))

print("Reward mean: {:4.2f}".format(reward_sum / number_validation_runs))
print("Finished")
print(num_levels_solved)
