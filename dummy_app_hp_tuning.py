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
    environment_configuration["number_buttons_horizontal"] = 5
    environment_configuration["number_buttons_vertical"] = 5
    environment_configuration["buttons_size_horizontal"] = 50
    environment_configuration["buttons_size_vertical"] = 30
    

    brain_configuration = dict()
    brain_configuration["type"] = random.choice(["CTRNN", "CTRNN", "CTRNN", "CTRNN", "ELMANNN", "GRUNN", "LSTMNN", "FFNN"])

    if(brain_configuration["type"] == "CTRNN"):
        brain_configuration["differential_equation"] = random.choice(["NaturalNet", "LiHoChow2005"])

        if(brain_configuration["differential_equation"] == "NaturalNet"):
            brain_configuration["set_principle_diagonal_elements_of_W_negative"] = random.choice([False, True])

        elif(brain_configuration["differential_equation"] == "LiHoChow2005"):
            brain_configuration["set_principle_diagonal_elements_of_W_negative"] = False
            brain_configuration["alpha"] = random.choice([0.0, 0.1, 0.01])

        else:
            raise RuntimeError("No valid CTRNN differential equation")

        brain_configuration["delta_t"] = 0.05
        brain_configuration["number_neurons"] = random.choice([5, 10, 20, 50])
        brain_configuration["clipping_range"] = random.choice([1.0, 3.0, float('inf'), float('inf')])
        brain_configuration["optimize_x0"] = True

    elif(brain_configuration["type"] == "ELMANNN" or brain_configuration["type"] == "GRUNN" or brain_configuration["type"] == "LSTMNN"):
        brain_configuration["hidden_layer_structure"] = random.choice([[5], [10], [20], [50]])
        brain_configuration["use_bias"] = True

    elif(brain_configuration["type"] == "FFNN"):
        brain_configuration["hidden_layers"] = random.choice([[5, 5], [10, 10], [20, 20], [50, 50]])
        brain_configuration["neuron_activation"] = "tanh"
        brain_configuration["neuron_activation_output"] = "tanh"
        brain_configuration["use_bias"] = True

    else:
        raise RuntimeError("No valid brain type")

    optimizer_configuration = dict()
    optimizer_configuration["type"] = "CMA-ES-Deap"
    optimizer_configuration["population_size"] = 200
    optimizer_configuration["sigma"] = random.choice([0.5, 1.0, 2.0])

    configuration = dict()
    configuration["number_generations"] = 2500
    configuration["number_validation_runs"] = 50
    configuration["number_rounds"] = 5
    configuration["maximum_env_seed"] = 100000
    configuration["environment"] = environment_configuration
    configuration["brain"] = brain_configuration
    configuration["optimizer"] = optimizer_configuration

    print(configuration)

    # Path of current script
    script_directory = Path(__file__).parent.absolute()

    train(configuration, results_directory=os.path.join(script_directory, 'results'))
