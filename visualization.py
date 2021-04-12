import json
import time
import os
import numpy as np

from brains.i_brain import get_brain_class
from environments.i_environment import get_environment_class

directory = os.path.join('Simulation_Results', '2021-03-25_11-18-39')

# Load configuration file
with open(os.path.join(directory, 'Configuration.json'), "r") as read_file:
    configuration = json.load(read_file)

individual = np.load(os.path.join(directory, 'Best_Genome.npy'), allow_pickle=True)

environment_class = get_environment_class(configuration['environment']['type'])
env = environment_class(env_seed=0, configuration=configuration['environment'])

brain_class = get_brain_class(configuration['brain']['type'])
brain_state = brain_class.load_brain_state(os.path.join(directory, 'Brain_State.npz'))

brain = brain_class(input_size=env.get_number_inputs(),
                    output_size=env.get_number_outputs(),
                    individual=individual,
                    configuration=configuration['brain'],
                    brain_state=brain_state)

number_validation_runs = configuration['number_validation_runs']

fitness_total = 0

# W_np = brain.W.toarray()

for env_seed in range(number_validation_runs):

    env = environment_class(env_seed=env_seed, configuration=configuration['environment'])

    ob = env.reset()
    brain.reset()

    fitness_current = 0
    done = False

    while not done:
        action = brain.step(ob)
        ob, rew, done, info = env.step(action)
        fitness_current += rew

        env.render()
        time.sleep(0.005)

    fitness_total += fitness_current

    print("Seed: {}   Reward:  {:4.2f}".format(env_seed, fitness_current))

print("Reward mean: {:4.2f}".format(fitness_total / number_validation_runs))
print("Finished")
