import numpy as np
import math


class OptimizerCanonicalEs:

    def __init__(self, individual_size: int, offspring_population_size: int, parent_population_size: int, step_size):
        self.policy = np.zeros(individual_size)
        self.offspring_population_size = offspring_population_size

        self.w = self.get_reward_weights(parent_population_size)
        self.step_size = step_size
        self.genomes = []

    def ask(self):
        self.genomes = []
        for _ in range(self.offspring_population_size):
            genome = self.policy + self.step_size * np.random.randn(self.individual_size).astype(np.float32)
            self.genomes.append(genome)

        return self.genomes

    def tell(self, rewards):
        # Sort rewards in descending order
        sorted_rewards = np.flip(np.argsort(rewards)).flatten()

        # Update policy
        for i in range(self.parent_population_size):
            j = sorted_rewards[i]
            self.policy += self.step_size * self.w[i] * self.genomes[j]

    @staticmethod
    def get_reward_weights(population_size):
        mu = population_size

        w_denominator = 0
        for j in range(mu):
            w_denominator += math.log(mu + 0.5) - math.log(j + 1)

        w = np.asarray([(math.log(mu + 0.5) - math.log(i + 1)) / w_denominator for i in range(mu)])

        return w
