from optimizer.i_optimizer import IOptimizer
import attr
import numpy as np


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerOpenAIESCfg:
    type: str
    population_size: int
    learning_rate: np.float32
    sigma: np.float32


class OptimizerOpenAIES(IOptimizer):
    def __init__(self, individual_size: int, configuration: dict):
        self.noise = []
        self.random_state = np.random.RandomState(seed=0)
        self.individual_size = individual_size
        self.configuration = OptimizerOpenAIESCfg(**configuration)
        self.current_individual = self.initialize_individual(std=1.0)

        self.population_size = self.configuration.population_size
        self.learning_rate = self.configuration.learning_rate
        self.sigma = self.configuration.sigma

    def initialize_individual(self, std=1.0):
        """
        This initializes the individual when first starting the optimizer. OpenAI used this in their implementation
        and Experiments showed that this could be a factor for the performance of the algorithm.

        Source: https://github.com/openai/evolution-strategies-starter

        :param std:
        :return:
        """
        out = np.random.randn(self.individual_size).astype(np.float32)
        out *= std / np.sqrt(np.square(out).sum(axis=0, keepdims=True))

        return out

    def ask(self):
        individuals = []
        for i in range(self.population_size):
            noise_for_individual = self.random_state.randn(self.individual_size)
            noisy_individual = self.current_individual + noise_for_individual

            self.noise.append(noise_for_individual)
            individuals.append(noisy_individual)

        return individuals

    def tell(self, rewards):
        weighted_noise = np.sum([n * r for (n, r) in zip(self.noise, rewards)], axis=0, dtype=np.float32)
        update = (self.learning_rate / (self.population_size * self.sigma)) * weighted_noise
        self.current_individual = self.current_individual + update

        self.noise = []
