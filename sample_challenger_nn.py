from naturalnets.train import train
import random

while True:

    challenger_network_configuration = dict()
    challenger_network_configuration["type"] = "FeedForwardNN"
    challenger_network_configuration["hidden_layers"] = [8, 4]
    challenger_network_configuration["neuron_activation"] = "tanh"
    challenger_network_configuration["neuron_activation_output"] = "tanh"
    challenger_network_configuration["use_bias"] = True

    environment_configuration = dict()
    environment_configuration["type"] = "ChallengerNeuralNetwork"
    environment_configuration["number_inputs"] = 10
    environment_configuration["number_outputs"] = 3
    environment_configuration["exclude_reward_from_observation"] = random.choice([False, True])
    environment_configuration["number_time_steps"] = 1000
    environment_configuration["brain"] = challenger_network_configuration

    brain_configuration = dict()
    brain_configuration["type"] = "CTRNN"
    brain_configuration["differential_equation"] = "NaturalNet"
    brain_configuration["set_principle_diagonal_elements_of_W_negative"] = False
    brain_configuration["delta_t"] = 0.05
    brain_configuration["number_neurons"] = 20
    brain_configuration["clipping_range"] = 1.0
    brain_configuration["optimize_x0"] = False

    optimizer_configuration = dict()
    optimizer_configuration["type"] = "CmaEsDeap"
    optimizer_configuration["population_size"] = 50
    optimizer_configuration["sigma"] = 1.0

    configuration = dict()
    configuration["number_generations"] = 2500
    configuration["number_validation_runs"] = 50
    configuration["number_rounds"] = 10
    configuration["maximum_env_seed"] = 10000
    configuration["environment"] = environment_configuration
    configuration["brain"] = brain_configuration
    configuration["optimizer"] = optimizer_configuration
    configuration["enhancer"] = {"type": None}
    configuration["global_seed"] = random.randint(0, 1000)

    train(configuration, results_directory="results")