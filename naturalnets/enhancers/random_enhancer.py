from typing import Optional, Tuple, Dict

import cv2
import numpy as np
from numpy.random import default_rng

from naturalnets.enhancers.i_enhancer import IEnhancer, register_enhancer_class


@register_enhancer_class
class RandomEnhancer(IEnhancer):

    def __init__(self, env_output_size: int, rng_seed: int = None):
        super().__init__(env_output_size)
        self.rng = default_rng(seed=rng_seed)
        self.brain_output = None

    def get_number_outputs(self) -> int:
        return self.env_output_size

    @staticmethod
    def render_visualization_ellipses(image: np.ndarray, brain_output: np.ndarray, screen_width: int,
                                      screen_height: int, color: Tuple[int, int, int]):
        if brain_output.shape == (4,):
            # Visualize the action distribution as an ellipse
            action_position_x = int(0.5 * (brain_output[0] + 1.0) * screen_width)
            action_position_y = int(0.5 * (brain_output[1] + 1.0) * screen_height)
            action_distribution_x = abs(int(0.5 * brain_output[2] * screen_width))
            action_distribution_y = abs(int(0.5 * brain_output[3] * screen_height))
            image = cv2.ellipse(
                image,
                (action_position_x, action_position_y),
                (action_distribution_x, action_distribution_y),
                angle=0, startAngle=0, endAngle=360, color=color, thickness=1
            )

        return image

    def reset(self, rng_seed: int = None):
        self.rng = default_rng(seed=rng_seed)

    def step(self, brain_output) -> Tuple[np.ndarray, Optional[Dict[str, np.ndarray]]]:
        self.brain_output = brain_output
        return np.tanh(
            brain_output[:self.env_output_size]
            + (brain_output[self.env_output_size:] * self.rng.standard_normal(size=self.env_output_size))
        ), {"random_enhancer_info": brain_output}
