import csv
import json
import logging
import os

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

LOG_KIND_JSON = "log_kind_json"
LOG_KIND_TXT = "log_kind_txt"


def read_simulations(base_directory):
    simulation_runs = []
    for sub_dir in os.listdir(base_directory):
        simulation_folder = os.path.join(base_directory, sub_dir)

        conf = None

        try:
            with open(os.path.join(simulation_folder, "Configuration.json"), "r") as read_file:
                conf = json.load(read_file)
        except FileNotFoundError:
            logging.error("Could not read configuration for {}".format(simulation_folder))

        log = None
        log_kind = None

        try:
            with open(os.path.join(simulation_folder, "Log.json"), "r") as read_file:
                log = json.load(read_file)
                log_kind = LOG_KIND_JSON
        except FileNotFoundError:
            pass

        if log is None:
            # If log could not be parsed as JSON try a txt file which works but is certainly more error prone
            try:
                with open(os.path.join(simulation_folder, "Log.txt"), "r") as log_file:
                    log = log_file.readlines()
                    log_kind = LOG_KIND_TXT
            except FileNotFoundError:
                logging.error("Could not read log for {}".format(simulation_folder))

        plot_path = os.path.join(simulation_folder, "plot.png")
        if os.path.isfile(plot_path):
            plot_path = "=HYPERLINK(\"" + plot_path + "\")"
        else:
            logging.warning("No plot found for {}".format(simulation_folder))
            plot_path = None

        sim = {
            "dir": sub_dir,
            "conf": conf,
            "log": {"log": log, "log_kind": log_kind},
            "plot": plot_path,
        }
        simulation_runs.append(sim)
    return simulation_runs


# TODO remove this once we have newer experiments with JSON logs again
def read_log_from_txt_file(log_txt):
    delimiter_counter = 0
    starting_index = -1
    for i, log_entry in enumerate(log_txt):
        if log_entry == "------------------------------------------------------------------------------------------\n":
            delimiter_counter += 1

            if delimiter_counter == 2:
                starting_index = i + 1
                break

    if starting_index == -1 or starting_index >= len(log_txt):
        return None

    # Remove "preamble", and the last two lines which is a line break and the elapsed time of the experiment
    log_txt = log_txt[starting_index:-2]

    for i, log_entry in enumerate(log_txt):
        # Log entries are printed in strings, splitting and casting to float creates a list of numerical values
        split_log_entry = log_entry.split()

        if len(split_log_entry) != 6:
            # Sometimes minimum values are so low that they "touch" the next column, which results in split()
            # merging the minimum and mean value as they are next to each other in the log. Simple solution is to
            # don't include this log
            return None

        log_txt[i] = [float(sub_entry) for sub_entry in split_log_entry]

    return log_txt


def gather_info_for_csv(simulation):
    log_dict = simulation["log"]
    log = log_dict["log"]
    log_kind = log_dict["log_kind"]
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

        # Layout of Log.txt is
        # ['gen', 'min', 'mean', 'max', 'best', 'elapsed time (s)\n']
        if log_kind == LOG_KIND_JSON:
            mean = [log_entry["mean"] for log_entry in log]
            maximum = [log_entry["max"] for log_entry in log]
            best = [log_entry["best"] for log_entry in log]

        elif log_kind == LOG_KIND_TXT:
            log = read_log_from_txt_file(log)

            if log is None:
                logging.warning("Log could not be parsed from TXT file for {}".format(sim_directory))
                return

            mean = [log_entry[2] for log_entry in log]
            maximum = [log_entry[3] for log_entry in log]
            best = [log_entry[4] for log_entry in log]

        else:
            logging.warning("Log is not present as JSON or TXT file")
            return

        generations = [i for i in range(len(log))]

    try:
        brain = conf["brain"]
        optimizer = conf["optimizer"]
        environment = conf["environment"]
        # Delete them from config because leaving them in config would print the values twice
        del conf["brain"]
        del conf["optimizer"]
        del conf["environment"]
    except KeyError:
        logging.warning("Could not locate brain, optimizer or environment in config.")
        brain = {}
        optimizer = {}
        environment = {}

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
