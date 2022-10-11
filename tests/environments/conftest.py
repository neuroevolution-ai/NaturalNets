from typing import List

import numpy as np
import pytest


@pytest.fixture
def test_coordinates_and_rewards() -> List[np.ndarray]:
    coordinates_and_rewards = [
        np.load("test-coordinates-and-reward.npy"),
        np.load("test-coordinates-and-reward-2.npy"),
        np.load("test-coordinates-and-reward-3.npy")
    ]

    return coordinates_and_rewards
