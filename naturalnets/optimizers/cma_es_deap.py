from typing import Union

import numpy as np
from attrs import define, field, validators
from deap import base
from deap import cma
from deap import creator

from naturalnets.optimizers.i_optimizer import IOptimizer, IOptimizerCfg, register_optimizer_class


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerCmaEsDeapCfg(IOptimizerCfg):
    # population_size must be >= 3, otherwise PyCMA will raise a warning that an additional individual is injected
    population_size: int = field(validator=[validators.instance_of(int), validators.ge(3)])
    sigma: Union[int, float] = field(validator=[validators.instance_of((int, float))])


@register_optimizer_class
class CmaEsDeap(IOptimizer):

    def __init__(self, individual_size: int, configuration: dict):

        self.individual_size = individual_size
        config = OptimizerCmaEsDeapCfg(**configuration)

        try:
            del creator.Individual
            del creator.FitnessMax
        except AttributeError:
            # They do not exist, thus simply continue
            pass

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, typecode="b", fitness=creator.FitnessMax)

        strategy = cma.Strategy(centroid=[0.0] * individual_size, sigma=config.sigma, lambda_=config.population_size)

        self.toolbox = base.Toolbox()
        self.toolbox.register("generate", strategy.generate, creator.Individual)
        self.toolbox.register("update", strategy.update)

        self.population = None

    def ask(self):
        # Generate a new population
        self.population = self.toolbox.generate()
        genomes = []
        for individual in self.population:
            genomes.append(np.array(individual))

        return genomes

    def tell(self, rewards):
        for ind, fit in zip(self.population, rewards):
            ind.fitness.values = (fit,)

        # Update the strategy with the evaluated individuals
        self.toolbox.update(self.population)
