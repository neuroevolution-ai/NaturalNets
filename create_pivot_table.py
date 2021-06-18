import numpy as np
import pandas as pd


def apply_robotics_filters(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[data["conf.experiment_id"] == 1]
    filtered_data = filtered_data[filtered_data["brain.type"] == "CTRNN"]
    filtered_data = filtered_data[filtered_data["environment.type"] == "GymMujoco"]

    return filtered_data


def apply_global_filters(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[data["conf.experiment_id"] == 1]
    filtered_data = filtered_data[filtered_data["brain.type"] == "CTRNN"]

    return filtered_data


def round_pivot_table(pivot_table: pd.DataFrame, environments: list):
    # Integers look better in the paper therefore we first round and then cast to remove trailing zeros (except for
    # the average time)
    for env in environments:
        pivot_table[env] = pivot_table[env].round({"best_mean": 0,
                                                   "best_amax": 0,
                                                   "best_len": 0,
                                                   "elapsed_time_mean": 1})

        # TODO this will for some reason not work
        # pivot_table[env] = pivot_table[env].astype({"maximum_average_mean": np.int32,
        #                                             "maximum_average_amax": np.int32,
        #                                             "maximum_average_len": np.int32,
        #                                             "elapsed_time_mean": np.float32})

    return pivot_table


def create_pivot_table_row(data: pd.DataFrame, row_property: str, environments: list,
                           order_of_columns: list) -> pd.DataFrame:
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

        per_env_pivot_tables.append(env_pivot_table)

    # Concatenate the individual pivot tables horizontally, i.e. this will be one row in the final pivot table
    pivot_table_row = pd.concat(per_env_pivot_tables, keys=environments, axis=1)

    return pivot_table_row


def add_total_row(pivot_table: pd.DataFrame, environments: list, order_of_columns: list,
                  total_row_functions: list) -> pd.DataFrame:
    # This simply says apply this function to that column, i.e. apply max to the column where we list max values
    # because we want the maximum reward over all the rows in the pivot table
    aggregate_functions = {col: col_fun for (col, col_fun) in zip(order_of_columns, total_row_functions)}

    total_row = []

    for env in environments:
        per_env_data = pivot_table[env]

        total_row.append(per_env_data.agg(aggregate_functions))

    total_row_values = pd.concat(total_row).values

    pivot_table.loc["Total", :] = total_row_values

    return pivot_table


def format_latex(latex_formatted_pivot_table: pd.DataFrame, row_names):
    # TODO column_format is not agnostic to how many environments are compared
    latex = latex_formatted_pivot_table.to_latex(escape=False, column_format="|r||c|c|c|c||c|c|c|c||c|c|c|c|")

    for concrete_row_name in row_names[1:]:
        latex = latex.replace("\\\n{}".format(concrete_row_name), "\\ \hline \n{}".format(concrete_row_name))

    # Also draw a row line for the total row
    latex = latex.replace("\\\n\\textbf{Total:}", "\\ \hline \n\\textbf{Total:}")

    return latex


def format_for_latex(pivot_table: pd.DataFrame, row_properties, row_names):
    # TODO
    #  1. Row Index flatten und Empty Rows einfügen
    #  2. Empty Rows umbennen -> jeweils in die Config Property so wie sie in der LaTeX Tabelle stehen soll
    #       Die Namen abspeichern, braucht man später für die hlines
    #  3. Dann die anderen Rows umbennen -> nur noch die Zahl z.B. oder True/False soll dastehen
    #  4. Dann die \hlines einfügen

    modified_pivot_table = add_empty_rows(pivot_table, row_properties=row_properties, row_names=row_names)

    return modified_pivot_table


def add_empty_rows(pivot_table: pd.DataFrame, row_properties, row_names):
    # Für jeden key in row_properties brauchen wir eine empty row
    # 1. neue empty row erstellen
    # 2. name ändern -> So steht es später in der Tabelle
    # Dann alle umordnen an die richtige Stelle

    modified_pivot_table = pivot_table.copy()

    modified_pivot_table.index = modified_pivot_table.index.to_flat_index()

    # This is used to check later if the reindexing worked properly
    original_index_size = len(modified_pivot_table.index)

    # Could fail but then again why would you format an empty pivot table
    empty_row = pivot_table.iloc[0].astype(str)

    for i in range(len(empty_row)):
        empty_row[i] = ""

    for row_prop in row_properties:
        current_empty_row = empty_row.copy()
        current_empty_row.name = row_prop

        modified_pivot_table = modified_pivot_table.append(current_empty_row)

    # Reorder the rows so that the newly added empty rows are directly above their respective property of the experiment
    reordered_index = [None] * len(modified_pivot_table.index)

    current_prop = None
    i = 0  # Index for iterating through the current index as it is in the pivot table
    j = -1  # Index for the new index list

    # Basically iterates through the modified index (the empty rows are at the back). As the empty rows are named like
    # the properties that are listed first in the tuple (e.g. (optimizer.population_size, 100)), we can use this to
    # sort of break there, insert the empty row and then use j to insert the actual rows with data. This way i will
    # increase until it reached the original index size (as it looks only on the original rows) and j increases to
    # the size of the new index, as it is used to insert the rows into this new index.
    while i < len(modified_pivot_table.index):
        index_entry = modified_pivot_table.index[i]
        if current_prop is None or current_prop != index_entry[0]:
            current_prop = index_entry[0]
            j += 1
            reordered_index[j] = current_prop

        i += 1
        j += 1

        if j >= len(reordered_index):
            break

        reordered_index[j] = index_entry

    # Check if the running variables have been successfully increased to its desired size
    assert j == len(reordered_index) and i == original_index_size

    modified_pivot_table = modified_pivot_table.reindex(reordered_index)

    rename_mapping_index = {}

    # Now rename the rows with a pretty name, use j to index row_names
    j = 0
    for i, index_entry in enumerate(modified_pivot_table.index):
        if not isinstance(index_entry, tuple):
            if index_entry == "Total":
                # Handle the Total row separately which has no value in the second item of the tuple
                rename_mapping_index[index_entry] = "\textbf{Total:}"
            else:
                rename_mapping_index[index_entry] = row_names[j]
                j += 1
        else:
            # Take the second item from the tuple which is equal to the value set for the property, e.g. 100 in
            # (optimizer.population_size, 100)
            rename_mapping_index[index_entry] = index_entry[1]

    # Asserts that all row_names have been applied
    assert j == len(row_names)

    modified_pivot_table = modified_pivot_table.rename(index=rename_mapping_index)

    return modified_pivot_table


def main():
    experiments_data = pd.read_csv("spreadsheets/output.csv")

    # Filters used for each part of the pivot table (e.g. neural network used is CTRNN, ...)
    globally_filtered_data = apply_robotics_filters(experiments_data)

    environments = ["Hopper-v2", "HalfCheetah-v2", "Walker2d-v2"]
    row_properties = ["optimizer.population_size", "brain.number_neurons", "brain.clipping_range",
                      "brain.set_principle_diagonal_elements_of_W_negative", "optimizer.sigma"]

    # Pretty names which is used later when creating the LaTeX table
    row_names = [
        "$\lambda$ (Population Size):",
        "$N_n$ (Number Neurons):",
        "$c$ (Clipping Range):",
        "$W_{xx}\_negative$:",
        "$\sigma$ (Initial Deviation):"
    ]

    column_order = ["best_mean", "best_amax", "best_len", "conf.elapsed_time_mean"]
    # This has to match column_order, as these functions will be used on the columns to calculate the total row values
    total_row_functions = [np.mean, np.max, len, np.mean]

    rows = []

    for row_prop in row_properties:
        rows.append(create_pivot_table_row(globally_filtered_data,
                                           row_property=row_prop,
                                           environments=environments,
                                           order_of_columns=column_order))

    # Create the overall pivot table
    pivot_table = pd.concat(rows, keys=row_properties, axis=0)

    pivot_table = add_total_row(pivot_table, environments, column_order, total_row_functions)

    pivot_table = round_pivot_table(pivot_table, environments)

    pivot_table.to_csv("spreadsheets/pivot_table.csv")

    # pivot_table.to_latex("spreadsheets/pivot_table.tex")
    latex_formatted_pivot_table = format_for_latex(pivot_table, row_properties=row_properties, row_names=row_names)
    latex = format_latex(latex_formatted_pivot_table, row_names)

    with open("spreadsheets/pivot_table.tex", "w") as latex_file:
        latex_file.write(latex)


if __name__ == "__main__":
    main()
