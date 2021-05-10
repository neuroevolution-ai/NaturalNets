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


def generate_filter(experiment_data: pd.DataFrame, filters: List[Tuple], bitwise_and=True, existing_filters=None):
    last_filter = None

    if existing_filters is not None:
        last_filter = existing_filters

    for (label, value) in filters:
        current_filter = experiment_data[label] == value

        if last_filter is None:
            last_filter = current_filter
            continue

        if bitwise_and:
            last_filter = last_filter & current_filter
        else:
            # Use bitwise or, used if multiple values per column shall be used
            last_filter = last_filter | current_filter

    return last_filter


def combine_columns(experiment_data: pd.DataFrame, columns: List[str], unpack_last_column=False):
    altered_data = experiment_data.copy()

    if unpack_last_column:
        altered_data[columns[-1]] = experiment_data[columns[-1]].apply(lambda x: x if np.isnan(x) else np.sum(x))

    assert len(columns) >= 2

    for col in columns[1:]:
        altered_data[columns[0]] = altered_data[columns[0]].fillna(altered_data[col])

    altered_data = altered_data.drop(columns=columns[1:])

    return altered_data


def create_pivot_table(table: pd.DataFrame, group_by_column: Union[List[str], str], columns: List,
                       filters=None):
    filtered_data = table

    if filters is not None:
        filtered_data = table[filters]

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


def generate_ctrnn_pivot_table(_dir_path, experiment_data: pd.DataFrame):
    filters = [("brain.type", "CTRNN"), ("environment.type", "CollectPoints"), ("environment.use_sensors", True)]
    filters = generate_filter(experiment_data, filters, bitwise_and=True)
    base_columns = ["mavg", "max", "best"]

    pivot_table_number_neurons = create_pivot_table(experiment_data,
                                                    group_by_column="brain.number_neurons",
                                                    columns=base_columns + ["brain.number_neurons"],
                                                    filters=filters)

    pivot_table_diff_eq = create_pivot_table(experiment_data,
                                             group_by_column="brain.differential_equation",
                                             columns=base_columns + ["brain.differential_equation"],
                                             filters=filters)

    pivot_table_clipping = create_pivot_table(experiment_data,
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

    merged_pivots.to_csv(os.path.join(dir_path, "ctrnn_pivot_table.csv"))

    # Pandas has a nice feature to generate LaTeX tables from a DataFrame
    merged_pivots.to_latex(os.path.join(dir_path, "ctrnn_pivot_table.tex"))

    total_row = total_row.round().astype(int)
    total_row = total_row.rename(columns=cleaner_column_names)

    total_row.to_csv(os.path.join(dir_path, "ctrnn_total_row.csv"))
    total_row.to_latex(os.path.join(dir_path, "ctrnn_total_row.tex"))


def generate_network_comparison_pivot_table(_dir_path, experiment_data: pd.DataFrame):
    filters_brain_type = [("brain.type", "CTRNN"),
                          ("brain.type", "ELMANNN"),
                          ("brain.type", "GRUNN"),
                          ("brain.type", "LSTMNN")]
    filters = generate_filter(experiment_data, filters=filters_brain_type, bitwise_and=False)

    filters_general = [("environment.type", "CollectPoints"), ("environment.use_sensors", True)]
    filters = generate_filter(experiment_data, filters=filters_general, bitwise_and=True, existing_filters=filters)

    base_columns = ["mavg", "max", "best"]

    # Merge the columns for the number of neurons for CTRNNs and Elman/LSTM/GRU, also unpack as for the last mentioned
    # networks the number of neurons is saved as a list but we want floats, i.e. this will sum up the entries of
    # brain.hidden_layer_structure
    # altered_data = combine_columns(experiment_data,
    #                                columns=["brain.number_neurons", "brain.hidden_layer_structure"],
    #                                unpack_last_column=True)
    #
    # pivot_table_number_neurons = create_pivot_table(altered_data,
    #                                                 group_by_column="brain.number_neurons",
    #                                                 columns=base_columns + ["brain.number_neurons"],
    #                                                 filters=filters)

    # filters = generate_filter(experiment_data, filters=filters_general + [("brain.type", "CTRNN")], bitwise_and=True)
    pivot_table_architecture_comparison = create_pivot_table(experiment_data,
                                                             group_by_column="brain.type",
                                                             columns=base_columns + ["brain.type"],
                                                             filters=filters)

    pivot_table_architecture_comparison = pivot_table_architecture_comparison.round().astype(int)

    rename_architectures = {
        "CTRNN": "NeuralNet",
        "ELMANNN": "Elman",
        "GRUNN": "GRU",
        "LSTMNN": "LSTM"
    }

    cleaner_column_names = {"mavg": "Mean Reward",
                            "max": "Max Reward",
                            "best": "Best Reward"}

    pivot_table_architecture_comparison = pivot_table_architecture_comparison.rename(index=rename_architectures,
                                                                                     columns=cleaner_column_names)

    pivot_table_architecture_comparison.to_csv(os.path.join(_dir_path, "architecture_comparison_pivot_table.csv"))
    pivot_table_architecture_comparison.to_latex(os.path.join(_dir_path, "architecture_comparison_pivot_table.tex"))


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

experiments_dataframe = pd.DataFrame(data, columns=keys)
experiments_dataframe.to_csv(output_file_name)

generate_ctrnn_pivot_table(dir_path, experiment_data=experiments_dataframe)
generate_network_comparison_pivot_table(dir_path, experiment_data=experiments_dataframe)

logging.info("Log and pivot tables written to the following folder {}".format(dir_path))
