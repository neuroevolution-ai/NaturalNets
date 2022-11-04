from typing import Union

import cma
from attrs import define, field, validators

from naturalnets.optimizers.i_optimizer import IOptimizer, IOptimizerCfg, register_optimizer_class


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerCmaEsPyCmaCfg(IOptimizerCfg):
    population_size: int = field(validator=[validators.instance_of(int)])
    sigma: Union[int, float] = field(validator=[validators.instance_of((int, float)), validators.gt(0)])


@register_optimizer_class
class CmaEsPyCma(IOptimizer):

    def __init__(self, individual_size: int, global_seed: int, configuration: dict):
        super().__init__(individual_size, global_seed, configuration)

        config = OptimizerCmaEsPyCmaCfg(**self.config_dict)

        self.es = cma.CMAEvolutionStrategy(
            x0=[0.0] * self.individual_size,
            sigma0=config.sigma,
            inopts={"popsize": config.population_size}
        )

        self.solutions = None

    def ask(self):
        self.solutions = self.es.ask()
        return self.solutions

    def tell(self, rewards):
        self.es.tell(self.solutions, rewards)
