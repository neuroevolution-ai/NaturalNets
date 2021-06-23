import pandas as pd
import numpy as np


def main():
    experiments_data = pd.read_csv("../../spreadsheets/output.csv")

    # Filters used for each part of the pivot table (e.g. neural network used is CTRNN, ...)
    # For example 'robotic' is experiment_id==1, brain.type==CTRNN and environment.type==GymMujoco
    globally_filtered_data = apply_global_filters(experiments_data, "robotics")

    environments = ["Hopper-v2", "HalfCheetah-v2", "Walker2d-v2"]

    # These will basically be the rows of the pivot table. Each row of the final pivot table will be a value that these
    # properties have during an experiment (e.g. if population size was chosen to be 50, a row with that will be in the
    # pivot table)
    row_properties = ["optimizer.population_size", "brain.number_neurons", "brain.clipping_range",
                      "brain.set_principle_diagonal_elements_of_W_negative", "optimizer.sigma"]

    # The next variables define which functions and properties to use to aggregate on for creating the pivot table.
    # In our case it makes the most sense to use the property 'best' as these are the best individuals and
    # 'conf.elapsed_time' to show how long an experiment runs

    # Defines the order of the columns, i.e. the order in this list resembles the order of the columns
    column_order = ["best_mean", "best_amax", "best_len", "conf.elapsed_time_mean"]

    aggregate_functions_per_index = {
        "best_mean": np.mean,
        "best_amax": np.max,
        "best_len": np.sum,
        "conf.elapsed_time_mean": np.mean
    }

    aggregate_functions_for_all_indices = {
        "best_mean": np.mean,
        "best_amax": np.max,
        "best_len": np.mean,
        "conf.elapsed_time_mean": np.mean
    }

    round_mapper = {}
    type_mapper = {}
    for env in environments:
        for col in column_order:
            if not col == "conf.elapsed_time_mean":
                round_mapper[(env, col)] = 0
                type_mapper[(env, col)] = int
            else:
                # 1 means the rounding precision here, i.e. for the elapsed time we want for example 1,2 hours
                round_mapper[(env, col)] = 1

    rows = []

    row_property_types = {
        "brain.number_neurons": int
    }

    for row_prop in row_properties:
        try:
            row_prop_type = row_property_types[row_prop]
        except KeyError:
            row_prop_type = None
        rows.append(create_pivot_table_row(globally_filtered_data,
                                           row_property=row_prop,
                                           environments=environments,
                                           order_of_columns=column_order,
                                           row_property_type=row_prop_type))

    # Create the overall pivot table
    pivot_table = pd.concat(rows, keys=row_properties, axis=0)

    pivot_table = add_total_row(pivot_table, environments=environments, row_properties=row_properties,
                                aggregate_functions_per_index=aggregate_functions_per_index,
                                aggregate_functions_for_all_indices=aggregate_functions_for_all_indices)

    pivot_table = round_pivot_table(pivot_table, round_mapper=round_mapper, type_mapper=type_mapper)

    pivot_table.to_csv("spreadsheets/pivot_table.csv")


#############################################################################################
# Filters
#############################################################################################


def apply_global_filters(data: pd.DataFrame, filter: str) -> pd.DataFrame:
    if filter == "robotics":
        return _apply_robotics_filters(data)
    elif filter == "generic_ctrnn":
        return _apply_generic_ctrnn_filters(data)
    else:
        raise RuntimeError("Chosen global filter '{}' is not known, please choose another.".format(filter))


def _apply_robotics_filters(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[data["conf.experiment_id"] == 1]
    filtered_data = filtered_data[filtered_data["brain.type"] == "CTRNN"]
    filtered_data = filtered_data[filtered_data["environment.type"] == "GymMujoco"]

    return filtered_data


def _apply_generic_ctrnn_filters(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[data["conf.experiment_id"] == 1]
    filtered_data = filtered_data[filtered_data["brain.type"] == "CTRNN"]

    return filtered_data


#############################################################################################
# Pivot Table Creation
#############################################################################################


def create_pivot_table_row(data: pd.DataFrame, row_property: str, environments: list,
                           order_of_columns: list, row_property_type=None) -> pd.DataFrame:
    per_env_pivot_tables = []

    for env in environments:
        locally_filtered_data = data[data["environment.name"] == env]
        env_pivot_table = pd.pivot_table(locally_filtered_data,
                                         values=["best", "conf.elapsed_time"],
                                         index=[row_property],
                                         aggfunc={"best": [np.mean, np.max, len], "conf.elapsed_time": np.mean})

        # This simply flattens the column names because the pivot table functions returns them in a hierarchy
        env_pivot_table.columns = env_pivot_table.columns.to_series().str.join("_")

        # Now explicitly reorder the columns to be sure that they are in correct order
        env_pivot_table = env_pivot_table.reindex(
            columns=order_of_columns)

        # Convert elapsed time from seconds to hours
        env_pivot_table["conf.elapsed_time_mean"] = env_pivot_table["conf.elapsed_time_mean"] / 3600.0

        if row_property_type is not None:
            env_pivot_table.index = env_pivot_table.index.astype(row_property_type)

        per_env_pivot_tables.append(env_pivot_table)

    # Concatenate the individual pivot tables horizontally, i.e. this will be one row in the final pivot table
    pivot_table_row = pd.concat(per_env_pivot_tables, keys=environments, axis=1)

    return pivot_table_row


def add_total_row(pivot_table: pd.DataFrame, environments: list, row_properties: list,
                  aggregate_functions_per_index: dict, aggregate_functions_for_all_indices: dict) -> pd.DataFrame:
    # This simply says apply this function to that column, i.e. apply max to the column where we list max values
    # because we want the maximum reward over all the rows in the pivot table
    total_row = []

    for env in environments:
        per_env_data = pivot_table[env]

        per_env_results = []
        for row_prop in row_properties:
            per_env_results.append(per_env_data.loc[row_prop].agg(aggregate_functions_per_index))

        total_row.append(pd.DataFrame(per_env_results).agg(aggregate_functions_for_all_indices))

    total_row_values = pd.concat(total_row).values

    pivot_table.loc["Total", :] = total_row_values

    return pivot_table


def round_pivot_table(pivot_table: pd.DataFrame, round_mapper: dict, type_mapper: dict):
    rounded_pivot_table = pivot_table.round(round_mapper).astype(type_mapper)

    return rounded_pivot_table


if __name__ == "__main__":
    main()
