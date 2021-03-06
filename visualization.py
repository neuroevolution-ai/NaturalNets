import gym
import json
import time
import cv2
import os
from brains.continuous_time_rnn import *

directory = os.path.join('Simulation_Results', '2021-03-06_07-11-49')

# Load configuration file
with open(os.path.join(directory, 'Configuration.json'), "r") as read_file:
    configuration = json.load(read_file)

brain_state = ContinuousTimeRNN.load_brain_state(os.path.join(directory, 'Brain_State.npz'))

individual = np.load(os.path.join(directory, 'Best_Genome.npy'), allow_pickle=True)

brain = ContinuousTimeRNN(individual=individual, configuration=configuration['brain'],
                                  brain_state=brain_state)


reward_sum = 0
number_validation_runs = 100

num_levels_solved = 0

for env_seed in range(number_validation_runs):

    env = gym.make('procgen:procgen-heist-v0', num_levels=1, start_level=env_seed, distribution_mode="memory")
    ob = env.reset()

    reward = 0
    done = False

    brain.reset()

    while not done:
        action = brain.step(ob.flatten() / 255.0)
        #ob, rew, done, info = env.step(np.argmax(action))

        ob, rew, done, info = env.step(env.action_space.sample())

        #obs = cv2.resize(ob, (20, 20), interpolation=cv2.INTER_AREA)

        cv2.imshow("ProcGen Agent", cv2.resize(ob, (500, 500)))
        cv2.waitKey(1)

        time.sleep(0.01)

        reward += rew

    reward_sum += reward
    print(reward)

    if reward > 0:
        num_levels_solved += 1

    print("Seed: {}   Reward:  {:4.2f}".format(env_seed, reward))

print("Reward mean: {:4.2f}".format(reward_sum/number_validation_runs))
print("Finished")
print(num_levels_solved)

