import json
import os
import shutil

import numpy as np

from naturalnets.tools.parse_experiments import read_simulations, parse_log

test_base_directory = "tests/test_simulation_base_dir"
test_experiment_directory = "test_exp"


def create_test_csv():
    # Log structure from train.py is:
    # ['gen', 'min', 'mean', 'max', 'best', 'elapsed time (s)\n']
    log = []
    for i in range(1000):
        log_entry = {
            "gen": i,
            "min": np.random.randn(),
            "mean": np.random.randn(),
            "max": np.random.randn(),
            "best": np.random.randn(),
            "elapsed time (s)": np.random.randn()
        }

        log.append(log_entry)

    os.makedirs(os.path.join(test_base_directory, test_experiment_directory), exist_ok=True)

    # Write log additionally to JSON for better parsing
    with open(os.path.join(test_base_directory, test_experiment_directory, "Log.json"), "w") as outfile:
        json.dump(log, outfile)

    return log


def test_parse_log():
    # Creates a random log, returns it as a dict and saves it as Log.json
    reference_log = create_test_csv()

    # Only use these values since parse_log() only returns these
    reference_generations = [log_entry["gen"] for log_entry in reference_log]
    reference_mean = [log_entry["mean"] for log_entry in reference_log]
    reference_maximum = [log_entry["max"] for log_entry in reference_log]
    reference_best = [log_entry["best"] for log_entry in reference_log]

    simulations = read_simulations(test_base_directory)

    assert len(simulations) == 1

    # Now parse the log which is extracted from the saved Log.json
    parsed_log = parse_log(simulations[0]["log"])

    assert np.array_equal(parsed_log["generations"], reference_generations)
    assert np.array_equal(parsed_log["mean"], reference_mean)
    assert np.array_equal(parsed_log["maximum"], reference_maximum)
    assert np.array_equal(parsed_log["best"], reference_best)

    # Remove the created test file and directory structure
    shutil.rmtree(test_base_directory)


if __name__ == "__main__":
    test_parse_log()
