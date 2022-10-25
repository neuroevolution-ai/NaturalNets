from naturalnets.train import train
import os
import random
from pathlib import Path

while True:

    environment_configuration = dict()
    environment_configuration["type"] = "DummyApp"
    environment_configuration["number_time_steps"] = 100
    environment_configuration["screen_width"] = 400
    environment_configuration["screen_height"] = 400
    environment_configuration["number_button_columns"] = 5
    environment_configuration["number_button_rows"] = 5
    environment_configuration["button_width"] = 50
    environment_configuration["button_height"] = 30
    environment_configuration["fixed_env_seed"] = True
    

    brain_configuration = dict()
    brain_configuration["type"] = random.choice(["RNN", "GRU", "LSTM", "FeedForwardNN"])

    if (brain_configuration["type"] == "RNN"
            or brain_configuration["type"] == "GRU"
            or brain_configuration["type"] == "LSTM"):
        brain_configuration["hidden_layers"] = random.choice([[5], [10], [20], [50]])
        brain_configuration["use_bias"] = True

    elif brain_configuration["type"] == "FeedForwardNN":
        brain_configuration["hidden_layers"] = random.choice([[5, 5], [10, 10], [20, 20], [50, 50]])
        brain_configuration["neuron_activation"] = "tanh"
        brain_configuration["neuron_activation_output"] = "tanh"
        brain_configuration["use_bias"] = True
    else:
        raise RuntimeError("No valid brain type")

    optimizer_configuration = dict()
    optimizer_configuration["type"] = "CmaEsDeap"
    optimizer_configuration["population_size"] = 200
    optimizer_configuration["sigma"] = random.choice([0.5, 1.0, 2.0])

    configuration = dict()
    configuration["number_generations"] = 5000
    configuration["number_validation_runs"] = 50
    configuration["number_rounds"] = random.choice([1, 3, 5, 10])
    configuration["maximum_env_seed"] = 100000
    configuration["environment"] = environment_configuration
    configuration["brain"] = brain_configuration
    configuration["optimizer"] = optimizer_configuration
    configuration["enhancer"] = {
        "type": [None, "RandomEnhancer"]
    }

    print(configuration)

    # Path of current script
    script_directory = Path(__file__).parent.absolute()

    train(configuration, results_directory=os.path.join(script_directory, 'results'))
