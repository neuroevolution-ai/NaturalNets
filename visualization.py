import json
import time
import os
import numpy as np

from naturalnets.brains.i_brain import get_brain_class
from naturalnets.enhancers.i_enhancer import get_enhancer_class, DummyEnhancer
from naturalnets.environments.i_environment import get_environment_class

directory = os.path.join('Simulation_Results', '2022-02-18_12-08-14')

# Load configuration file
with open(os.path.join(directory, 'Configuration.json'), "r") as read_file:
    configuration = json.load(read_file)

individual = np.load(os.path.join(directory, 'Best_Genome.npy'), allow_pickle=True)

environment_class = get_environment_class(configuration['environment']['type'])
env = environment_class(configuration=configuration['environment'])

if "enhancer" in configuration:
    enhancer_class = get_enhancer_class(configuration["enhancer"]["type"])
else:
    enhancer_class = DummyEnhancer

enhancer = enhancer_class(env.get_number_outputs())

brain_class = get_brain_class(configuration['brain']['type'])
brain_state = brain_class.load_brain_state(os.path.join(directory, 'Brain_State.npz'))

brain = brain_class(input_size=env.get_number_inputs(),
                    output_size=env.get_number_outputs() + enhancer.get_number_outputs(),
                    individual=individual,
                    configuration=configuration['brain'],
                    brain_state=brain_state)

number_validation_runs = configuration['number_validation_runs']

fitness_total = 0

# W_np = brain.W.toarray()

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
        time.sleep(0.005)

    fitness_total += fitness_current

    print("Seed: {}   Reward:  {:4.2f}".format(env_seed, fitness_current))

print("Reward mean: {:4.2f}".format(fitness_total / number_validation_runs))
print("Finished")
