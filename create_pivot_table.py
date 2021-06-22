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


def round_pivot_table(pivot_table: pd.DataFrame, round_mapper: dict, type_mapper: dict):
    rounded_pivot_table = pivot_table.round(round_mapper).astype(type_mapper)

    return rounded_pivot_table


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


def replace_column_names(latex: str, environments: list) -> str:
    index_start = latex.find("\\toprule") + len("\\toprule")
    index_end = latex.rfind("\\midrule")

    inner_slice = latex[latex.find("\\toprule") + len("\\toprule"):latex.rfind("\\midrule")]

    index_inner_start = inner_slice.find("\\\\\n{}") + len("\\\\\n{}")
    index_inner_end = inner_slice.rfind("\\\\\n")

    # test_slice_shorter = inner_slice[inner_slice.find("\\\\\n{}") + len("\\\\\n{}"):inner_slice.rfind("\\\\\n")]

    col_names_upper_row = """& Reward & Reward &       & Avg"""
    col_names_lower_row = """& Mean   & Max    & Count & Time"""

    reformatted_output = ""

    for i in range(len(environments)):
        reformatted_output += col_names_upper_row

    reformatted_output += "\\\ \n"

    for i in range(len(environments)):
        reformatted_output += col_names_lower_row

    output_first_part = latex[:index_start]
    output_second_part = latex[index_start:index_start + index_inner_start]

    # TODO need to replace the column format in the multicolumns so that the environment is centered
    # output_second_part2 = output_second_part.replace("}{l}")

    output_third_part = reformatted_output
    output_forth_part = latex[index_start + index_inner_end:index_end]
    output_fifth_part = latex[index_end:]

    output_latex = output_first_part + output_second_part + output_third_part + output_forth_part + output_fifth_part

    return output_latex


def insert_parameter_column_name(latex: str):
    # Later there is actually a '{}' after the Parameter but since LaTeX treats this as sort of an empty block I guess,
    # it doesn't matter
    modified_latex = latex.replace("\\toprule\n", "\\toprule\n \\textbf{Parameter}")

    return modified_latex


def format_environment_columns(latex: str, environments: list, column_order: list):
    modified_latex = latex

    i = 0
    while i < len(environments):

        find_str = "\\multicolumn{" + str(len(column_order)) + "}{l}{\\textbf{" + str(environments[i]) + "}"

        if i == len(environments) - 1:
            # Last environment (i.e. the last column) only has 'c|' as the format (only one '|')
            replace_str = "\\multicolumn{" + str(len(column_order)) + "}{c|}{\\textbf{" + str(environments[i]) + "}"
        else:
            replace_str = "\\multicolumn{" + str(len(column_order)) + "}{c||}{\\textbf{" + str(environments[i]) + "}"

        modified_latex = modified_latex.replace(find_str, replace_str)

        i += 1

    assert i == len(environments)

    return modified_latex


def format_latex(latex_formatted_pivot_table: pd.DataFrame, row_names, environments, column_order):
    # TODO column_format is not agnostic to how many environments are compared
    latex = latex_formatted_pivot_table.to_latex(escape=False, column_format="|r||c|c|c|c||c|c|c|c||c|c|c|c|")

    for concrete_row_name in row_names[1:]:
        latex = latex.replace("\\\n{}".format(concrete_row_name), "\\ \hline \n{}".format(concrete_row_name))

    # Also draw a row line for the total row
    latex = latex.replace("\\\n\\textbf{Total:}", "\\ \hline \n\\textbf{Total:}")

    latex = replace_column_names(latex, environments)
    latex = insert_parameter_column_name(latex)
    latex = format_environment_columns(latex, environments=environments, column_order=column_order)

    # This fixes the lines. Without that the lines would not be drawed through
    latex = latex.replace("\\toprule", "\\hline")
    latex = latex.replace("\\midrule", "\\hline")
    latex = latex.replace("\\bottomrule", "\\hline")

    return latex


def rename_environment_columns(pivot_table: pd.DataFrame, new_environment_column_names: dict) -> pd.DataFrame:
    renamed_pivot_table = pivot_table.rename(columns=new_environment_column_names)

    return renamed_pivot_table


def format_elapsed_time_column(pivot_table: pd.DataFrame, environments: list) -> pd.DataFrame:
    modified_pivot_table = pivot_table.copy()

    for env in environments:
        modified_pivot_table.loc[:, (env, "conf.elapsed_time_mean")] = pivot_table.loc[:, (env, "conf.elapsed_time_mean")].astype(str) + " h"

    return modified_pivot_table


def make_total_row_bold(pivot_table: pd.DataFrame) -> pd.DataFrame:
    modified_pivot_table = pivot_table.copy()
    modified_pivot_table.loc[("Total", "")] = "\textbf{" + modified_pivot_table.loc[("Total", "")].astype(str) + "}"

    return modified_pivot_table


def format_for_latex(pivot_table: pd.DataFrame, row_properties, row_names, new_environment_column_names, environments):
    # TODO
    #  1. Row Index flatten und Empty Rows einfügen
    #  2. Empty Rows umbennen -> jeweils in die Config Property so wie sie in der LaTeX Tabelle stehen soll
    #       Die Namen abspeichern, braucht man später für die hlines
    #  3. Dann die anderen Rows umbennen -> nur noch die Zahl z.B. oder True/False soll dastehen
    #  4. Dann die \hlines einfügen
    #  5. \toprule, \midrule und \bottomrule ersetzen mit \hline

    modified_pivot_table = format_elapsed_time_column(pivot_table, environments)
    modified_pivot_table = make_total_row_bold(modified_pivot_table)
    modified_pivot_table = add_empty_rows(modified_pivot_table, row_properties=row_properties, row_names=row_names)
    modified_pivot_table = rename_environment_columns(modified_pivot_table, new_environment_column_names)

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

            if current_prop == "Total":
                # The total row has a tuple ("Total", "") and this whole tuple needs to be set so that the reindexing
                # finds this row later
                reordered_index[j] = index_entry
            else:
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
            rename_mapping_index[index_entry] = row_names[j]
            j += 1
        else:
            if index_entry == ("Total", ""):
                # Handle the Total row separately which has no value in the second item of the tuple
                rename_mapping_index[index_entry] = "\textbf{Total:}"
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

    new_environment_column_names = {
        "Hopper-v2": "\textbf{Hopper-v2} ($\Delta t = 0.008\,s$)",
        "HalfCheetah-v2": "\textbf{HalfCheetah-v2} ($\Delta t = 0.05\,s$)",
        "Walker2d-v2": "\textbf{Walker2d-v2} ($\Delta t = 0.008\,s$)"
    }

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

    for row_prop in row_properties:
        rows.append(create_pivot_table_row(globally_filtered_data,
                                           row_property=row_prop,
                                           environments=environments,
                                           order_of_columns=column_order))

    # Create the overall pivot table
    pivot_table = pd.concat(rows, keys=row_properties, axis=0)

    pivot_table = add_total_row(pivot_table, environments=environments, row_properties=row_properties,
                                aggregate_functions_per_index=aggregate_functions_per_index,
                                aggregate_functions_for_all_indices=aggregate_functions_for_all_indices)

    pivot_table = round_pivot_table(pivot_table, round_mapper=round_mapper, type_mapper=type_mapper)

    pivot_table.to_csv("spreadsheets/pivot_table.csv")

    # pivot_table.to_latex("spreadsheets/pivot_table.tex")
    latex_formatted_pivot_table = format_for_latex(pivot_table, row_properties=row_properties, row_names=row_names,
                                                   new_environment_column_names=new_environment_column_names,
                                                   environments=environments)
    latex = format_latex(latex_formatted_pivot_table, row_names=row_names, environments=environments,
                         column_order=column_order)

    with open("spreadsheets/pivot_table.tex", "w") as latex_file:
        latex_file.write(latex)


if __name__ == "__main__":
    main()
