import subprocess
import json
import random

optimization_configuration_keys = ["environment",
                                   "neural_network_type",
                                   "random_seed_for_environment",
                                   "population_size",
                                   "number_generations",
                                   "sigma",
                                   "number_fitness_runs"]

lnn_configuration_keys = ["use_biases", "number_neurons_layer1"]

lstm_configuration_keys = ["hidden_layer_structure", "diagonal_hidden_to_hidden", "use_bias"]

ctrnn_configuration_keys = ["number_neurons",
                            "delta_t",
                            "optimize_state_boundaries",
                            "clipping_range",
                            "optimize_y0",
                            "set_principle_diagonal_elements_of_W_negative"]

with open('Stop_Optimization.json', 'w') as outfile:
    json.dump({"stop_optimization": False}, outfile)

stop_optimization = False

print("Optimization started")

while not stop_optimization:

    with open("configurations/Mujoco_CMA-ES_CTRNN_Design_Space.json", "r") as readfile:
        configuration = json.load(readfile)


    def sample_from_design_space(node):
        result = {}
        for key in node:
            val = node[key]
            if isinstance(val, list):
                if val:
                    val = random.sample(val, 1)[0]
                else:
                    # empty lists become None
                    val = None

            if isinstance(val, dict):
                result[key] = sample_from_design_space(val)
            else:20
                result[key] = val
        return result


    configuration_out = sample_from_design_space(configuration)

    with open('configurations/Configuration.json', 'w') as outfile:
        json.dump(configuration_out, outfile, indent=4)

    with open("Stop_Optimization.json", "r") as readfile:
        d = json.load(readfile)
        stop_optimization = d["stop_optimization"]

    subprocess.run(["python", "train.py"])

print("Optimization finished")
