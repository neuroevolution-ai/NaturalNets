import json
import logging
import os


def read_simulations(base_directory):
    simulation_runs = []

    for sub_dir in os.listdir(base_directory):
        simulation_folder = os.path.join(base_directory, sub_dir)

        with open(os.path.join(simulation_folder, "Configuration.json"), "r") as read_file:
            conf = json.load(read_file)

        with open(os.path.join(simulation_folder, "Log.json"), "r") as read_file:
            log = json.load(read_file)

        sim = {"dir": sub_dir, "conf": conf, "log": log}
        simulation_runs.append(sim)

    return simulation_runs


def gather_info_for_csv(simulation):
    conf = simulation["conf"]

    brain = {"brain." + k: v for k, v in conf["brain"].items()}
    optimizer = {"optimizer." + k: v for k, v in conf["optimizer"].items()}
    environment = {"environment." + k: v for k, v in conf["environment"].items()}

    # Delete them from config because leaving them in config would print the values twice
    del conf["brain"]
    del conf["optimizer"]
    del conf["environment"]

    conf = {"conf." + k: v for k, v in conf.items()}

    log = simulation["log"]

    # Last element of log contains additional info like elapsed time for training
    log_info = log.pop()

    mean = [log_entry["mean"] for log_entry in log]
    maximum = [log_entry["max"] for log_entry in log]
    best = [log_entry["best"] for log_entry in log]

    return {"gen": len(log),
            "mavg": max(mean),
            "max": max(maximum),
            "best": max(best),
            "directory": simulation["dir"],
            "elapsed_time_training": log_info["elapsed_time_training"],
            "elapsed_time_training [h]": log_info["elapsed_time_training"]/3600,
            "CPU": log_info["cpu"],
            **conf, **brain, **optimizer, **environment}
