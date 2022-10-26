import random
from typing import Dict

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


def flatten_dict(config: Dict, prefix: str = "") -> Dict:
    flattened_dict = {}

    for k, v in config.items():
        if isinstance(v, dict):
            inner_flattened_dict = flatten_dict(v, prefix=k + "_")

            # Check if the inner_flattened_dict has keys that are already present in the main dict. If so that is not
            # desired and will trigger the assertion
            old_length = len(flattened_dict)
            flattened_dict.update(inner_flattened_dict)
            # assert old_length + len(inner_flattened_dict) == len(flattened_dict), ("Duplicate keys when flattening the config dict")

        else:
            if v is None:
                # Tensorboard does not display pure None values, therefore use a string (which it does
                # display)
                v = "None"
            elif isinstance(v, list):
                v = ", ".join(str(list_entry) for list_entry in v)

            flattened_dict[prefix + k] = v

    return flattened_dict


def set_seeds(seed: int):
    np.random.seed(seed)
    random.seed(seed)
