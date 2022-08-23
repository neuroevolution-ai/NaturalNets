import numpy as np


def rescale_values(values: np.ndarray, previous_low: int, previous_high: int, new_low: int, new_high: int,
                   round_to_int: bool = False):
    """
    Rescales the values coming from the value range [previous_low, previous_high] to the value range
    [new_low, new_high].

    Calculation according to https://stackoverflow.com/a/929107

    If round_to_int is provided the rescaled values are rounded to integers.
    """
    rescaled_values = (((values - previous_low) * (new_high - new_low)) / (previous_high - previous_low)) + new_low

    if round_to_int:
        return np.rint(rescaled_values)
    return rescaled_values
