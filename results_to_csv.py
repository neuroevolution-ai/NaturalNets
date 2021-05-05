import csv
import logging
import os

from tools.parse_experiments import read_simulations, parse_log

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def gather_info_for_csv(simulation):
    log = simulation["log"]
    conf = simulation["conf"]
    sim_directory = os.path.join(simulations_directory, simulation["dir"])

    if not conf:
        logging.warning("Configuration does not exist for {}".format(sim_directory))
        return

    generations = [-1]
    mean = [0]
    maximum = [0]
    best = [0]

    if log:
        parsed_log = parse_log(log)

        if parsed_log is None:
            return

        generations = parsed_log["generations"]
        mean = parsed_log["mean"]
        maximum = parsed_log["maximum"]
        best = parsed_log["best"]
    try:
        brain = {"brain." + k: v for k, v in conf["brain"].items()}
        optimizer = {"optimizer." + k: v for k, v in conf["optimizer"].items()}
        environment = {"environment." + k: v for k, v in conf["environment"].items()}
        # Delete them from config because leaving them in config would print the values twice
        del conf["brain"]
        del conf["optimizer"]
        del conf["environment"]
    except KeyError:
        logging.warning("Could not locate brain, optimizer or environment in config.")
        brain = {}
        optimizer = {}
        environment = {}

    conf = {"conf." + k: v for k, v in conf.items()}

    return {"gen": str(max(generations)),
            "mavg": str(max(mean)),
            "max": str(max(maximum)),
            "best": str(max(best)),
            "directory": simulation["dir"],
            "plot": simulation["plot"],
            **conf, **brain, **optimizer, **environment}


logging.basicConfig()

simulations_directory = "Simulation_Results"
output_file_name = "output.csv"

data = []
keys = []
for found_simulation in read_simulations(simulations_directory):
    d = gather_info_for_csv(found_simulation)
    if d:
        data.append(d)
        keys += d.keys()

# Make keys unique while preserving order
keys = [x for i, x in enumerate(keys) if i == keys.index(x)]

with open(output_file_name, "w") as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)
    logging.info("Log written to {}".format(output_file_name))
