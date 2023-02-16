from typing import Optional, Tuple, Dict

import numpy as np
from attrs import define, field, validators
from numpy.random import default_rng

from naturalnets.enhancers.i_enhancer import IEnhancer, IEnhancerCfg, register_enhancer_class


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class PurelyRandomEnhancerCfg(IEnhancerCfg):
    random_noise_std: float = field(
        converter=float,
        validator=[validators.instance_of(float), validators.ge(0), validators.le(1.0)]
    )


@register_enhancer_class
class PurelyRandomEnhancer(IEnhancer):

    def __init__(self, config, env_output_size: int, rng_seed: int = None):
        super().__init__(config, env_output_size)

        self.config = PurelyRandomEnhancerCfg(**self.config_dict)
        self.rng = default_rng(seed=rng_seed)

    def get_number_outputs(self) -> int:
        return 0

    def reset(self, rng_seed: int = None):
        self.rng = default_rng(seed=rng_seed)

    def step(self, brain_output) -> Tuple[np.ndarray, Optional[Dict[str, np.ndarray]]]:
        # This check is needed although multiplying with 0.0 would not alter the result, we would need to apply
        # tanh everytime to ensure the value range. This is not needed if we do not alter brain_output, because
        # the brains already apply tanh (applying tanh twice changes the results)
        if self.config.random_noise_std != 0.0:
            randomized_brain_output = np.tanh(
                    brain_output + self.config.random_noise_std * self.rng.standard_normal(size=self.env_output_size)
            )
        else:
            randomized_brain_output = brain_output

        return randomized_brain_output, {}
