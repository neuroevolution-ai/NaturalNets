from functools import partial

import attr
import numpy as np
from deap import base
from deap import tools
from deap.algorithms import varOr

from optimizers.i_optimizer import IOptimizer, registered_optimizer_classes


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerMuLambdaCfg:
    type: str
    mu: int
    lambda_: int
    initial_gene_range: int
    mutpb: float


class FitnessMax(base.Fitness):
    weights = (1.0,)


class Individual(list):

    def __init__(self, *args):
        super().__init__(*args)
        self.fitness = FitnessMax()


class OptimizerMuLambda(IOptimizer):
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
            tools.cxOnePoint,
            tools.cxTwoPoint,
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
            return tools.mutGaussian(individual=ind1, mu=0, sigma=sigma, indpb=indpb)

        self.toolbox = base.Toolbox()
        self.toolbox.register("mate", mate)
        self.toolbox.register("mutate", fct_mutation_learned)
        self.toolbox.register("select", tools.selBest)

    def ask(self):
        self.offspring = varOr(self.population, self.toolbox, self.configuration.lambda_, 1 - self.configuration.mutpb,
                               self.configuration.mutpb)
        return self.offspring

    def tell(self, rewards):
        for individual, individual_reward in zip(self.offspring, rewards):
            individual.fitness = individual_reward

        self.population = self.toolbox.select(self.offspring, self.configuration.mu)


# TODO: Do this registration via class decorator
registered_optimizer_classes["Mu+Lambda-Deap"] = OptimizerMuLambda
