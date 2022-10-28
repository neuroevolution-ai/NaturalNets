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

    def __init__(self, individual_size: int, configuration: dict):

        self.individual_size = individual_size
        config = OptimizerCmaEsPyCmaCfg(**configuration)

        self.es = cma.CMAEvolutionStrategy(x0=[0.0] * individual_size, sigma0=config.sigma,
                                           inopts={"popsize": config.population_size})

        self.solutions = None

    def ask(self):
        self.solutions = self.es.ask()
        return self.solutions

    def tell(self, rewards):
        self.es.tell(self.solutions, rewards)
