import numpy as np
import pandas as pd

from .generate_pivot_table import generate_pivot_table
from .generate_latex_pivot_table import generate_latex_pivot_table


def main(experiment_csv_path: str = None):
    if experiment_csv_path is not None:
        experiments_data = pd.read_csv(experiment_csv_path)
    else:
        experiments_data = pd.read_csv("../../spreadsheets/output.csv")

    # Filters used for each part of the pivot table (e.g. neural network used is CTRNN, ...)
    # For example 'robotic' is experiment_id==1, brain.type==CTRNN and environment.type==GymMujoco
    filtered_experiments_data = apply_global_filters(experiments_data, global_filter_type="robotics")

    environments = ["Hopper-v2", "HalfCheetah-v2", "Walker2d-v2"]

    # These will basically be the rows of the pivot table. Each row of the final pivot table will be a value that these
    # properties have during an experiment (e.g. if population size was chosen to be 50, a row with that will be in the
    # pivot table)
    row_properties = ["optimizer.population_size", "brain.number_neurons", "brain.clipping_range", "brain.optimize_x0",
                      "brain.set_principle_diagonal_elements_of_W_negative", "optimizer.sigma"]

    # The next variables define which functions and properties to use to aggregate on for creating the pivot table.
    # In our case it makes the most sense to use the property 'best' as these are the best individuals and
    # 'conf.elapsed_time' to show how long an experiment runs

    # Defines the order of the columns, i.e. the order in this list resembles the order of the columns
    column_order = ["best_mean", "best_amax", "best_len", "conf.elapsed_time_mean"]

    # These functions will be used to aggregate per row property, for example when the part of the pivot table is
    # created for the row prop 'brain.number_neurons' then we want to take the np.max over all the best rewards for
    # the max column
    aggregate_functions_per_row_property = {
        "best_mean": np.mean,
        "best_amax": np.max,
        "best_len": np.sum,
        "conf.elapsed_time_mean": np.mean
    }

    # These functions are used to create the total row at the bottom of the pivot table. They are similar to
    # 'aggregate_functions_per_row_property' but for example for the column that counts how many experiments have been
    # done, np.sum would be misleading as this would sum over all row_properties. This would be wrong as this much
    # experiments have not been done but for each row_property the same amount of experiments have been done (this is
    # a property of the pivot table). If you don't understand this look at the 'Count' column in the generated pivot
    # table.
    aggregate_functions_over_all_row_properties = {
        "best_mean": np.mean,
        "best_amax": np.max,
        "best_len": np.mean,
        "conf.elapsed_time_mean": np.mean
    }

    # This simply defines the rounding precision per column. We want Integers for every column except for the column
    # with the estimated time, which shall have a precision of one (e.g. an experiment lasted 1,2 hours)
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

    # If some row properties have the wrong format in the final pivot table (e.g. brain.number_neurons is a float in
    # the table), define here the type it shall be rounded to.
    # Note that for "brain.set_principle_diagonal_elements_of_W_negative" this does not work as these are correctly
    # typed here but later when creating the LaTeX from the DataFrame they get messed up, so we have to correct this
    # when modifying the LaTeX part.
    row_property_types = {
        "brain.number_neurons": int
    }

    pivot_table = generate_pivot_table(filtered_experiments_data, row_properties=row_properties,
                                       row_property_types=row_property_types,
                                       environments=environments, column_order=column_order,
                                       aggregate_functions_per_row_property=aggregate_functions_per_row_property,
                                       aggregate_functions_over_all_row_properties=aggregate_functions_over_all_row_properties,
                                       round_mapper=round_mapper, type_mapper=type_mapper)

    contains_elapsed_time_column = True

    # Pretty names which is used later when creating the LaTeX table
    row_names = [
        "$\lambda$ (Population Size):",
        "$N_n$ (Number Neurons):",
        "$c$ (Clipping Range):",
        "$optimize\_x_0$:",
        "$W_{xx}\_negative$:",
        "$\sigma$ (Initial Deviation):"
    ]

    new_environment_column_names = {
        "Hopper-v2": "\textbf{Hopper-v2}",
        "HalfCheetah-v2": "\textbf{HalfCheetah-v2}",
        "Walker2d-v2": "\textbf{Walker2d-v2}"
    }

    rename_mapper = {
        ('brain.set_principle_diagonal_elements_of_W_negative', 1.0): "True",
        ('brain.optimize_x0', 1.0): "True"
    }

    # TODO as parameter
    col_names_upper_row = """& Reward & Reward &       & Avg"""
    col_names_lower_row = """& Mean   & Max    & Count & Time"""

    generate_latex_pivot_table(pivot_table, row_properties=row_properties, row_names=row_names,
                               new_environment_column_names=new_environment_column_names,
                               environments=environments, rename_mapper=rename_mapper, column_order=column_order,
                               col_names_upper_row=col_names_upper_row, col_names_lower_row=col_names_lower_row,
                               contains_elapsed_time_column=contains_elapsed_time_column)


#############################################################################################
# Filters
#############################################################################################


def apply_global_filters(data: pd.DataFrame, global_filter_type: str) -> pd.DataFrame:
    if global_filter_type == "robotics":
        return _apply_robotics_filters(data)
    elif global_filter_type == "generic_ctrnn":
        return _apply_generic_ctrnn_filters(data)
    else:
        raise RuntimeError("Chosen global filter '{}' is not known, please choose another.".format(global_filter_type))


def _apply_robotics_filters(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[data["conf.experiment_id"] == 1]
    filtered_data = filtered_data[filtered_data["brain.type"] == "CTRNN"]
    filtered_data = filtered_data[filtered_data["environment.type"] == "GymMujoco"]

    return filtered_data


def _apply_generic_ctrnn_filters(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[data["conf.experiment_id"] == 1]
    filtered_data = filtered_data[filtered_data["brain.type"] == "CTRNN"]

    return filtered_data


if __name__ == "__main__":
    main()
