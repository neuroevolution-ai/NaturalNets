import pandas as pd


def generate_latex_pivot_table(pivot_table: pd.DataFrame, row_properties, row_names, new_environment_column_names,
                               environments,
                               rename_mapper, column_order, col_names_upper_row, col_names_lower_row,
                               contains_elapsed_time_column: bool = True):
    modified_pivot_table = pivot_table

    if contains_elapsed_time_column:
        modified_pivot_table = _format_elapsed_time_column(modified_pivot_table, environments)

    modified_pivot_table = _make_total_row_bold(modified_pivot_table)

    modified_pivot_table = _add_empty_rows(modified_pivot_table, row_properties=row_properties, row_names=row_names,
                                           rename_mapper=rename_mapper)

    modified_pivot_table = _rename_environment_columns(modified_pivot_table, new_environment_column_names)

    # TODO column_format is not agnostic to how many environments are compared
    column_format = "|r|"

    for _ in range(len(environments)):
        column_format += "|c" * len(column_order)
        column_format += "|"

    latex = modified_pivot_table.to_latex(escape=False, column_format=column_format)

    modified_latex = _insert_separating_horizontal_lines(latex, row_names=row_names)
    modified_latex = _replace_column_names(modified_latex, environments=environments,
                                           col_names_upper_row=col_names_upper_row,
                                           col_names_lower_row=col_names_lower_row)
    modified_latex = _insert_parameter_in_upper_left_corner(modified_latex)
    modified_latex = _format_environment_columns(modified_latex, environments=environments, column_order=column_order)

    # This fixes the lines. Without that the lines would not be drawed through
    modified_latex = modified_latex.replace("\\toprule", "\\hline")
    modified_latex = modified_latex.replace("\\midrule", "\\hline")
    modified_latex = modified_latex.replace("\\bottomrule", "\\hline")

    with open("spreadsheets/pivot_table.tex", "w") as latex_file:
        latex_file.write(modified_latex)


#############################################################################################
# Modifications on the Pivot Table while it is still a pd.DataFrame
#############################################################################################


def _format_elapsed_time_column(pivot_table: pd.DataFrame, environments: list) -> pd.DataFrame:
    modified_pivot_table = pivot_table.copy()

    for env in environments:
        modified_pivot_table.loc[:, (env, "conf.elapsed_time_mean")] = pivot_table.loc[:, (env, "conf.elapsed_time_mean")].astype(str) + " h"

    return modified_pivot_table


def _make_total_row_bold(pivot_table: pd.DataFrame) -> pd.DataFrame:
    modified_pivot_table = pivot_table.copy()
    modified_pivot_table.loc[("Total", "")] = "\textbf{" + modified_pivot_table.loc[("Total", "")].astype(str) + "}"

    return modified_pivot_table


def _add_empty_rows(pivot_table: pd.DataFrame, row_properties, row_names, rename_mapper: dict):
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
                # Optionally also rename the value here, for example
                # ('brain.set_principle_diagonal_elements_of_W_negative', 1.0) always converts True to 1.0 but in the
                # table we want to have 'True', so we rename it here
                try:
                    rename_mapping_index[index_entry] = rename_mapper[index_entry]
                except KeyError:
                    rename_mapping_index[index_entry] = index_entry[1]

    # Asserts that all row_names have been applied
    assert j == len(row_names)

    modified_pivot_table = modified_pivot_table.rename(index=rename_mapping_index)

    return modified_pivot_table


def _rename_environment_columns(pivot_table: pd.DataFrame, new_environment_column_names: dict) -> pd.DataFrame:
    renamed_pivot_table = pivot_table.rename(columns=new_environment_column_names)

    return renamed_pivot_table


#############################################################################################
# Modifications on the LaTeX String (string modifications)
#############################################################################################


def _insert_separating_horizontal_lines(latex: str, row_names: list):
    modified_latex = latex

    # Start by the second row_name because for the first there is already a separating line (the line between the
    # column header and the first row)
    for concrete_row_name in row_names[1:]:
        modified_latex = modified_latex.replace("\\\n{}".format(concrete_row_name),
                                                "\\ \hline \n{}".format(concrete_row_name))

    # Also draw a row line for the total row
    modified_latex = modified_latex.replace("\\\n\\textbf{Total:}", "\\ \hline \n\\textbf{Total:}")

    return modified_latex


def _replace_column_names(latex: str, environments: list, col_names_upper_row, col_names_lower_row) -> str:
    index_start = latex.find("\\toprule") + len("\\toprule")
    index_end = latex.rfind("\\midrule")

    inner_slice = latex[latex.find("\\toprule") + len("\\toprule"):latex.rfind("\\midrule")]

    index_inner_start = inner_slice.find("\\\\\n{}") + len("\\\\\n{}")
    index_inner_end = inner_slice.rfind("\\\\\n")

    reformatted_output = ""

    for i in range(len(environments)):
        reformatted_output += col_names_upper_row

    reformatted_output += "\\\ \n"

    for i in range(len(environments)):
        reformatted_output += col_names_lower_row

    output_first_part = latex[:index_start]
    output_second_part = latex[index_start:index_start + index_inner_start]
    output_third_part = reformatted_output
    output_forth_part = latex[index_start + index_inner_end:index_end]
    output_fifth_part = latex[index_end:]

    output_latex = output_first_part + output_second_part + output_third_part + output_forth_part + output_fifth_part

    return output_latex


def _insert_parameter_in_upper_left_corner(latex: str):
    # Later there is actually a '{}' after the Parameter but since LaTeX treats this as sort of an empty block I guess,
    # it doesn't matter
    modified_latex = latex.replace("\\toprule\n", "\\toprule\n \\textbf{Parameter}")

    return modified_latex


def _format_environment_columns(latex: str, environments: list, column_order: list):
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
