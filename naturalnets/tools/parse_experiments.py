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

        plot_path = os.path.join(simulation_folder, "plot.svg")
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


def parse_log(log_dict):
    log = log_dict["log"]
    log_kind = log_dict["log_kind"]

    # Layout of Log.txt is
    # ['gen', 'min', 'mean', 'max', 'best', 'elapsed time (s)\n']
    if log_kind == LOG_KIND_JSON:
        mean = [log_entry["mean"] for log_entry in log]
        maximum = [log_entry["max"] for log_entry in log]
        best = [log_entry["best"] for log_entry in log]

    elif log_kind == LOG_KIND_TXT:
        log = read_log_from_txt_file(log)

        if log is None:
            logging.warning("Log could not be parsed from TXT file")
            return None

        mean = [log_entry[2] for log_entry in log]
        maximum = [log_entry[3] for log_entry in log]
        best = [log_entry[4] for log_entry in log]

    else:
        logging.warning("Log is not present as JSON or TXT file")
        return None

    generations = [i for i in range(len(log))]

    return {
        "generations": generations,
        "mean": mean,
        "maximum": maximum,
        "best": best
    }
