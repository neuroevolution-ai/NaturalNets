import logging
import os
from typing import List, Tuple, Union

import numpy as np
import pandas as pd

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

    return {"gen": max(generations),
            "mavg": max(mean),
            "max": max(maximum),
            "best": max(best),
            "directory": simulation["dir"],
            "plot": simulation["plot"],
            **conf, **brain, **optimizer, **environment}


def create_pivot_table(dir_path: str, table: pd.DataFrame, group_by_column: Union[List[str], str], columns: List,
                       filters: List[Tuple] = None):
    filtered_data = table

    if filters is not None:
        last_filter = None
        for (label, value) in filters:
            current_filter = table[label] == value

            if last_filter is None:
                last_filter = current_filter
                continue

            last_filter = last_filter & current_filter

        filtered_data = table[last_filter]

    filtered_data = filtered_data[columns]

    if isinstance(group_by_column, list):
        # This case is for clipping_min and clipping_max which will be displayed as one part of the table
        # "Clipping [-x, x]"
        assert len(group_by_column) == 2
        assert (filtered_data.groupby(group_by_column[0]).size().values ==
                filtered_data.groupby(group_by_column[1]).size().values)

        # Remove one of the group vales to not mess up with the other pivot tables
        filtered_data = filtered_data.drop(group_by_column[1], axis=1)

        grouped_data = filtered_data.groupby(group_by_column[0])
    else:
        grouped_data = filtered_data.groupby(group_by_column)

    output_mean = grouped_data.mean()
    output_mean.insert(0, "Count", grouped_data.size())

    # file_name = "".join([str(value) + "-" for _, value in filters]) + "---" + str(group_by_column) + ".csv"
    # output_mean.to_csv(os.path.join(dir_path, file_name))

    return output_mean


logging.basicConfig()

dir_path = "spreadsheets"
os.makedirs(dir_path, exist_ok=True)

simulations_directory = "Simulation_Results"
output_file_name = os.path.join(dir_path, "output.csv")

data = []
keys = []
for found_simulation in read_simulations(simulations_directory):
    d = gather_info_for_csv(found_simulation)
    if d:
        data.append(d)
        keys += d.keys()

# Make keys unique while preserving order
keys = [x for i, x in enumerate(keys) if i == keys.index(x)]

data_frame = pd.DataFrame(data, columns=keys)
data_frame.to_csv(output_file_name)

filters = [("brain.type", "CTRNN"), ("environment.type", "CollectPoints"), ("environment.use_sensors", True)]
base_columns = ["mavg", "max", "best"]

pivot_table_number_neurons = create_pivot_table(dir_path,
                                                data_frame,
                                                group_by_column="brain.number_neurons",
                                                columns=base_columns + ["brain.number_neurons"],
                                                filters=filters)

pivot_table_diff_eq = create_pivot_table(dir_path,
                                         data_frame,
                                         group_by_column="brain.differential_equation",
                                         columns=base_columns + ["brain.differential_equation"],
                                         filters=filters)

pivot_table_clipping = create_pivot_table(dir_path,
                                          data_frame,
                                          group_by_column=["brain.clipping_range_min", "brain.clipping_range_max"],
                                          columns=base_columns + ["brain.clipping_range_min",
                                                                  "brain.clipping_range_max"],
                                          filters=filters)

merged_pivots = pd.concat([pivot_table_number_neurons, pivot_table_diff_eq, pivot_table_clipping],
                          keys=["Number neurons", "Differential equation", "Clipping"])



# TODO total_row needs to be appended somehow
total_row = merged_pivots.groupby(level=0).agg(
    count=("Count", "sum"),
    mavg=("mavg", "mean"),
    max=("max", "mean"),
    best=("best", "mean")).reset_index().mean()

total_row = pd.DataFrame(np.expand_dims(total_row.to_numpy(), axis=0), columns=merged_pivots.columns)

# Use round + casting to integer because only casting does no proper rounding and without casting the values
# have .0 as a decimal place
merged_pivots = merged_pivots.round().astype(int)

cleaner_column_names = {"mavg": "Mean Reward",
                        "max": "Max Reward",
                        "best": "Best Reward"}
merged_pivots = merged_pivots.rename(columns=cleaner_column_names)

merged_pivots.to_csv(os.path.join(dir_path, "pivot_tables.csv"))

# Pandas has a nice feature to generate LaTeX tables from a DataFrame
merged_pivots.to_latex(os.path.join(dir_path, "pivot_table.tex"))

total_row = total_row.round().astype(int)
total_row = total_row.rename(columns=cleaner_column_names)

total_row.to_csv(os.path.join(dir_path, "total_row.csv"))
total_row.to_latex(os.path.join(dir_path, "total_row.tex"))

logging.info("Log and pivot tables written to the following folder {}".format(dir_path))
