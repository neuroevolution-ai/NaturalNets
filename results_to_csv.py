import csv
import json
import logging
import os

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


def read_simulations(base_directory):
    simulation_runs = []
    for sub_dir in os.listdir(base_directory):
        simulation_folder = os.path.join(base_directory, sub_dir)

        # noinspection PyBroadException
        try:
            with open(os.path.join(simulation_folder, "Configuration.json"), "r") as read_file:
                conf = json.load(read_file)
        except:
            conf = None
            logging.error("Could not read conf for " + str(simulation_folder), exc_info=True)

        # noinspection PyBroadException
        try:
            with open(os.path.join(simulation_folder, "Log.txt"), "r") as log_file:
                log = log_file.readlines()
        except Exception:
            log = None
            logging.error("couldn't read log for " + str(simulation_folder), exc_info=True)

        plot_path = os.path.join(simulation_folder, 'plot.png')
        if os.path.isfile(plot_path):
            # plot_path = os.path.abspath(plot_path)
            plot_path = "=HYPERLINK(\"" + plot_path + "\")"
        else:
            logging.warning("no plot found")
            plot_path = None

        sim = {
            "dir": sub_dir,
            "conf": conf,
            "log": log,
            "plot": plot_path,
        }
        simulation_runs.append(sim)
    return simulation_runs


def gather_info_for_csv(simulation):
    log = simulation["log"]
    conf = simulation["conf"]

    if not conf:
        logging.warning("conf doesn't exist.")
        return

    generations = [-1]
    minimum = [0]
    mean = [0]
    maximum = [0]
    best = [0]
    elapsed_time = [0]

    if log:
        delimiter_counter = 0
        starting_index = -1
        for i, log_entry in enumerate(log):
            if log_entry == "------------------------------------------------------------------------------------------\n":
                delimiter_counter += 1

                if delimiter_counter == 2:
                    starting_index = i + 1
                    break

        if starting_index == -1 or starting_index >= len(log):
            logging.warning("log could not be parsed")
            return

        # Remove "preamble", and the last two lines which is a line break and the elapsed time of the experiment
        log = log[starting_index:-2]

        for i, log_entry in enumerate(log):
            # Log entries are printed in strings, splitting and casting to float creates a list of numerical values
            splitted_log_entry = log_entry.split()

            if len(splitted_log_entry) != 6:
                # Sometimes minimum values are so low that they "touch" the next column, which results in split()
                # merging the minimum and mean value as they are next to each other in the log. Simple solution is to
                # don't include this log
                logging.warning("log could not be parsed")
                return

            log[i] = [float(sub_entry) for sub_entry in splitted_log_entry]

        generations = [i for i in range(len(log))]

        # Layout of Log.txt is
        # ['gen', 'min', 'mean', 'max', 'best', 'elapsed time (s)\n']

        minimum = [log_entry[1] for log_entry in log]
        mean = [log_entry[2] for log_entry in log]
        maximum = [log_entry[3] for log_entry in log]
        best = [log_entry[4] for log_entry in log]
        elapsed_time = [log_entry[5] for log_entry in log]

    try:
        brain = conf["brain"]
        optimizer = conf["optimizer"]
        environment = conf["environment"]
        # Delete them from config because leaving them in config would print the values twice
        del conf["brain"]
        del conf["optimizer"]
        del conf["environment"]
    except:
        logging.warning("could not locate brain, optimizer or ep_runner in conf.")
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
for simulation in read_simulations(simulations_directory):
    d = gather_info_for_csv(simulation)
    if d:
        data.append(d)
        keys += d.keys()

# make keys unique while preserving order
keys = [x for i, x in enumerate(keys) if i == keys.index(x)]

with open(output_file_name, "w") as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)
    logging.info("log written to " + str(output_file_name))
