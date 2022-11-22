import math
from typing import List

import numpy as np
from attrs import define, field, validators

from naturalnets.optimizers.i_optimizer import IOptimizer, IOptimizerCfg, register_optimizer_class


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerCanonicalEsCfg(IOptimizerCfg):
    # TODO update the validators once the optimizer is fixed
    offspring_population_size: int = field(validator=validators.instance_of(int))
    parent_population_size: int = field(validator=validators.instance_of(int))
    mutation_step_size: float = field(validator=validators.instance_of(float))


@register_optimizer_class
class CanonicalEs(IOptimizer):

    def __init__(self, individual_size: int, global_seed: int, configuration: dict, **kwargs):
        super().__init__(individual_size, global_seed, configuration, **kwargs)

        self.config = OptimizerCanonicalEsCfg(**self.config_dict)
        self.policy = np.zeros(self.individual_size)

        self.w = self.get_reward_weights(self.config.parent_population_size)
        self.genomes = []

    def ask(self):
        self.genomes = []
        for _ in range(self.config.offspring_population_size):
            genome = self.policy + self.config.mutation_step_size * np.random.randn(self.individual_size).astype(np.float32)
            self.genomes.append(genome)

        return self.genomes

    def tell(self, rewards: List[float]) -> np.ndarray:
        best_genome_current_generation = self.genomes[np.argmax(rewards)]

        # Sort rewards in descending order
        sorted_rewards = np.flip(np.argsort(rewards)).flatten()

        # TODO fix the optimizer: currently it only works if both population sizes are equal
        # Update policy
        for i in range(self.config.parent_population_size):
            j = sorted_rewards[i]
            self.policy += self.config.mutation_step_size * self.w[i] * self.genomes[j]

        return best_genome_current_generation

    @staticmethod
    def get_reward_weights(population_size):
        mu = population_size

        w_denominator = 0
        for j in range(mu):
            w_denominator += math.log(mu + 0.5) - math.log(j + 1)

        w = np.asarray([(math.log(mu + 0.5) - math.log(i + 1)) / w_denominator for i in range(mu)])

        return w
