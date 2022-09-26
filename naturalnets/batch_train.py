import json
import os
import random
import subprocess

TEMP_CONFIG_FILE = "naturalnets/configurations/temp-config.json"


def main():
    with open("naturalnets/Stop_Optimization.json", "w") as outfile:
        json.dump({"stop_optimization": False}, outfile)

    stop_optimization = False

    print("Optimization started")

    subconfiguration_counter = 0

    while not stop_optimization:

        with open("naturalnets/configurations/ID06_DummyApp_CMA-ES_Multiple_Brains_HP_Tuning.json", "r") as readfile:
            configuration = json.load(readfile)

        def sample_from_design_space(node):
            result = {}
            for key in node:
                val = node[key]
                if isinstance(val, list):
                    if val:
                        val = random.choice(val)
                    else:
                        # empty lists become None
                        val = None

                if isinstance(val, dict):
                    result[key] = sample_from_design_space(val)
                else:
                    result[key] = val
            return result

        # Get configuration from subconfiguration (optional)
        subconfigurations = []
        for i in range(100):
            key = "subconfiguration" + str(i)

            if key in configuration:
                subconfigurations.append(configuration[key])
                del configuration[key]

        if subconfigurations:
            # If list is not empty add subconfiguration by selecting a random subconfiguration from the list
            subconfiguration = subconfigurations[subconfiguration_counter % len(subconfigurations)]
            subconfiguration_counter += 1

            # Move configuration key value pairs to experiment
            for key, value in subconfiguration.items():
                configuration[key] = subconfiguration[key]

        # Get brain configs
        brains = []
        for i in range(10):
            key = "brain" + str(i)

            if key in configuration:
                brains.append(configuration[key])
                del configuration[key]

        if brains:
            # If list is not empty add brain to config by selecting a random brain from the list
            configuration["brain"] = random.choice(brains)

        configuration_out = sample_from_design_space(configuration)

        with open(TEMP_CONFIG_FILE, "w") as outfile:
            json.dump(configuration_out, outfile, indent=4)

        with open("naturalnets/Stop_Optimization.json", "r") as readfile:
            d = json.load(readfile)
            stop_optimization = d["stop_optimization"]

        subprocess.run(["python3", "naturalnets/train.py"])

    try:
        os.remove(TEMP_CONFIG_FILE)
    except FileNotFoundError:
        pass

    print("Optimization finished")


if __name__ == '__main__':
    main()
