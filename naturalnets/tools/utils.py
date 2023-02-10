import random
from typing import Dict

import numpy as np
import torch


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
            inner_flattened_dict = flatten_dict(v, prefix=f"{prefix}{k}_")

            # Check if the inner_flattened_dict has keys that are already present in the main dict. If so that is not
            # desired and will trigger the assertion
            old_length = len(flattened_dict)
            flattened_dict.update(inner_flattened_dict)
            assert old_length + len(inner_flattened_dict) == len(flattened_dict), ("Duplicate keys when flattening the "
                                                                                   "config dict")

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
    torch.manual_seed(seed)


class RunningStat(object):
    """
    Includes code from:
    evolution-strategies-starter Copyright (c) 2016 OpenAI (http://openai.com)

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
    rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
    Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
    OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    """

    def __init__(self, shape, eps):
        self.sum = np.zeros(shape, dtype=np.float32)
        self.sumsq = np.full(shape, eps, dtype=np.float32)
        self.count = eps

    def increment(self, s, ssq, c):
        self.sum += s
        self.sumsq += ssq
        self.count += c

    @property
    def mean(self):
        return self.sum / self.count

    @property
    def std(self):
        return np.sqrt(np.maximum(self.sumsq / self.count - np.square(self.mean), 1e-2))

    def set_from_init(self, init_mean, init_std, init_count):
        self.sum[:] = init_mean * init_count
        self.sumsq[:] = (np.square(init_mean) + np.square(init_std)) * init_count
        self.count = init_count
