from functools import partial
from typing import Union

import numpy as np
from attrs import define, field, validators
from deap import base
from deap import tools
from deap.algorithms import varOr

from naturalnets.optimizers.i_optimizer import IOptimizer, IOptimizerCfg, register_optimizer_class


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerMuLambdaCfg(IOptimizerCfg):
    # mu and lambda_ must be greater or equal to 2, as per the DEAP implementation
    mu: int = field(validator=[validators.instance_of(int), validators.ge(2)])
    lambda_: int = field(validator=[validators.instance_of(int), validators.ge(2)])
    initial_gene_range: Union[int, float] = field(validator=[validators.instance_of((int, float)), validators.gt(0)])

    # Probability that an offspring is produced by mutation; (1-mutpb) probability that crossover is used
    mutpb: float = field(validator=[validators.instance_of(float), validators.ge(0.0), validators.le(1.0)])


class FitnessMax(base.Fitness):
    weights = (1.0,)


class Individual(list):
    # TODO maybe change from float to np.float32 as increased precision is not necessary I think and would reduce
    #      computation time
    def __init__(self, *args):
        super().__init__(*args)
        self.fitness = FitnessMax()


@register_optimizer_class
class MuLambdaDeap(IOptimizer):
    def __init__(self, individual_size: int, configuration: dict) -> None:
        super().__init__()

        self.individual_size = individual_size
        self.configuration = OptimizerMuLambdaCfg(**configuration)

        self.indices = partial(np.random.uniform, -self.configuration.initial_gene_range,
                               self.configuration.initial_gene_range, individual_size)
        self.individual = partial(tools.initIterate, Individual, self.indices)
        self.population = tools.initRepeat(list, self.individual, n=self.configuration.mu)
        self.offspring = None

        mate_list = [
            tools.cxOnePoint,  # Executes a one point crossover
            tools.cxTwoPoint,  # Executes a two point crossover
        ]

        def mate(ind1, ind2):
            return np.random.choice(mate_list)(ind1, ind2)

        def fct_mutation_learned(ind1):
            # need to clip in up-direction because too large numbers create overflows
            # need to clip below to avoid stagnation, which happens when a top individuals
            # mutates bad strategy parameters
            ind1[-1] = np.clip(ind1[-1], -5, 3)
            ind1[-2] = np.clip(ind1[-2], -5, 3)
            sigma = 2 ** ind1[-1]
            indpb = 2 ** (ind1[-2] - 3)

            # mu here means 'mean' like in a gaussian distribution, sigma therefore standard deviation
            return tools.mutGaussian(individual=ind1, mu=0, sigma=sigma, indpb=indpb)

        self.toolbox = base.Toolbox()
        self.toolbox.register("mate", mate)
        self.toolbox.register("mutate", fct_mutation_learned)
        self.select = tools.selBest

    def ask(self):
        self.offspring = varOr(self.population, self.toolbox, self.configuration.lambda_, 1 - self.configuration.mutpb,
                               self.configuration.mutpb)

        genomes = []
        for individual in self.offspring:
            genomes.append(np.array(individual))

        return genomes

    def tell(self, rewards):
        for individual, individual_reward in zip(self.offspring, rewards):
            individual.fitness.values = tuple([individual_reward])

        self.population = self.select(self.offspring, self.configuration.mu)
