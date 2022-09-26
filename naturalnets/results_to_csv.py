import logging
import os
from typing import Dict, List

import pandas as pd

from naturalnets.tools.parse_experiments import read_simulations

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def parse_log(log: List[Dict]):
    return {
        "generations": [log_entry["gen"] for log_entry in log[:-1]],
        "mean": [log_entry["mean"] for log_entry in log[:-1]],
        "best": [log_entry["best"] for log_entry in log[:-1]],
        "maximum": [log_entry["max"] for log_entry in log[:-1]],
        "minimum": [log_entry["min"] for log_entry in log[:-1]]
    }


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

    return {"gen": max(generations),
            "mavg": max(mean),
            "max": max(maximum),
            "best": max(best),
            "directory": simulation["dir"],
            # "plot": simulation["plot"],  TODO remove or add feature again
            **conf, **brain, **optimizer, **environment}


logging.basicConfig()

dir_path = "spreadsheets"
os.makedirs(dir_path, exist_ok=True)

simulations_directory = "results"
output_file_name = os.path.join(dir_path, "Simulation_Results.csv")

data = []
keys = []
for found_simulation in read_simulations(simulations_directory):
    d = gather_info_for_csv(found_simulation)
    if d:
        data.append(d)
        keys += d.keys()

# Make keys unique while preserving order
keys = [x for i, x in enumerate(keys) if i == keys.index(x)]

experiments_dataframe = pd.DataFrame(data, columns=keys)
experiments_dataframe.to_csv(output_file_name)

logging.warning("Use other repo to create pivot tables if you need them")

logging.info("Log and pivot tables written to the following folder '{}'".format(dir_path))
