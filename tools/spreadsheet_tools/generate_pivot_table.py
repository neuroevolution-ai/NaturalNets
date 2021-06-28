import numpy as np
import pandas as pd


def generate_pivot_table(filtered_experiments_data: pd.DataFrame, row_properties, row_property_types, environments,
                         column_order, aggregate_functions_per_row_property,
                         aggregate_functions_over_all_row_properties,
                         round_mapper, type_mapper) -> pd.DataFrame:
    """
    Creates a pivot table for experiments.

    :param filtered_experiments_data: Pre-filtered data by experiment_id
    :param row_properties: These hyperparameters will be shown in the rows of the pivot table
    :param row_property_types: Can be used to define the type, which a row property shall have
    :param environments: Which environments shall be selected to construct the columns (environments used in training)
    :param column_order: Defines the order which the columns (per environment) shall have
    :param aggregate_functions_per_row_property: Functions to aggregate inside a row property
    :param aggregate_functions_over_all_row_properties: Functions to aggregate across row properties
    :param round_mapper: Defines to which precision the respective rows shall be rounded to
    :param type_mapper: Defines the type to which respective rows shall be casted to
    :return: A Pandas DataFrame containing the resulting pivot table, this can then be further formatted to a pivot
             table
    """
    rows = []

    for row_prop in row_properties:
        try:
            row_prop_type = row_property_types[row_prop]
        except KeyError:
            row_prop_type = None
        rows.append(create_pivot_table_row(filtered_experiments_data,
                                           row_property=row_prop,
                                           environments=environments,
                                           order_of_columns=column_order,
                                           row_property_type=row_prop_type))

    # Create the overall pivot table by appending them vertically
    pivot_table = pd.concat(rows, keys=row_properties, axis=0)

    # This calculates and then appends the total row to the end of the DataFrame
    pivot_table = add_total_row(pivot_table, environments=environments, row_properties=row_properties,
                                aggregate_functions_per_index=aggregate_functions_per_row_property,
                                aggregate_functions_for_all_indices=aggregate_functions_over_all_row_properties)

    # This rounds each column to the previously defined precision
    pivot_table = round_pivot_table(pivot_table, round_mapper=round_mapper, type_mapper=type_mapper)

    pivot_table.to_csv("../../spreadsheets/pivot_table.csv")

    return pivot_table


#############################################################################################
# Pivot Table Creation
#############################################################################################


def create_pivot_table_row(data: pd.DataFrame, row_property: str, environments: list,
                           order_of_columns: list, row_property_type=None) -> pd.DataFrame:
    """
    Creates one row of the pivot table, which may contain several sub-rows (exactly as many sub-rows as there are
    values that the respective row_property can be, e.g. if the row_property is 'number_neurons' there may be sub-rows
    for '10', '20', '50', etc.)

    :param data:
    :param row_property:
    :param environments:
    :param order_of_columns:
    :param row_property_type:
    :return:
    """
    per_env_pivot_tables = []

    for env in environments:
        locally_filtered_data = data[data["environment.name"] == env]

        # Note that the values are hardcoded here. This is somewhat restricting but these values are currently the best
        # one to use here. If this is changed, some lines down the conversion of the elapsed time from seconds to
        # hours need to be changed as well.
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
