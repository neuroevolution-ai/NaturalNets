"""
Includes code from:
evolution-strategies-starter Copyright (c) 2016 OpenAI (http://openai.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from collections import deque

import numpy as np
from attrs import define, field, validators

from naturalnets.optimizers.i_optimizer import IOptimizer, IOptimizerCfg, register_optimizer_class
from naturalnets.optimizers.openai_es.openai_es_utils import Adam, compute_centered_ranks, batched_weighted_sum


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerOpenAIESCfg(IOptimizerCfg):
    # Theoretically, population_size could be 1, but the individual is NaN in the first generation. Thus, assert >= 2
    population_size: int = field(validator=[validators.instance_of(int), validators.ge(2)])

    # Initial learning rate for the Adam optimizer
    learning_rate: float = field(validator=[validators.instance_of(float), validators.gt(0)])

    # Controls how much of the noise is added to the individual, i.e. this value is multiplied with the
    # sampled noise
    noise_stddev: float = field(validator=[validators.instance_of(float), validators.gt(0.0), validators.le(1.0)])

    # Controls the amount of weight decay, which is also called L2 regularization
    l2_regularization_coefficient: float = field(
        validator=[validators.instance_of(float), validators.ge(0.0), validators.le(1.0)]
    )

    # Mirrored sampling uses sampled noise twice, by adding and subtracting it to the current individual.
    # Note, that this does not double the population_size, because each added and subtracted perturbed individual
    # counts towards the population
    mirrored_sampling: bool = field(default=True, validator=validators.instance_of(bool))

    # Does not use the rewards directly, but ranks them and centers the ranked rewards between -0.5 and 0.5
    use_centered_ranks: bool = field(default=True, validator=validators.instance_of(bool))


@register_optimizer_class
class OpenAIEs(IOptimizer):
    def __init__(self, individual_size: int, global_seed: int, configuration: dict):
        super().__init__(individual_size, global_seed, configuration)

        self.rng = np.random.default_rng(seed=self.global_seed)

        self.configuration = OptimizerOpenAIESCfg(**self.config_dict)

        # TODO technically different std values are used for different hidden layers in the original implementation.
        #  A bit tricky to implement here, as we use also other brains instead of only feed forward.
        #  Specifically, std=1.0 is used for all hidden layers, and std=0.01 is used for the last layer which maps
        #  the previous calculations to the output
        self.current_individual = self.initialize_individual(std=1.0)

        self.population_size = self.configuration.population_size
        self.learning_rate = self.configuration.learning_rate
        self.adam = Adam(num_params=self.individual_size, stepsize=self.learning_rate)

        self.noise = []
        self.reward_history = deque(maxlen=10)
        self.last_mean_reward = 0

    def initialize_individual(self, std: float = 1.0):
        """
        This initializes the individual when first starting the optimizers. OpenAI used this in their implementation
        and experiments showed that this could be a factor for the performance of the algorithm.

        Source: https://github.com/openai/evolution-strategies-starter

        :param std:
        :return:
        """
        individual = self.rng.standard_normal(self.individual_size, dtype=np.float32)
        individual *= std / np.sqrt(np.square(individual).sum(axis=0, keepdims=True))

        return individual

    def adjust_learning_rate(self):
        if self.last_mean_reward is None:
            self.last_mean_reward = np.mean(self.reward_history)
            return

        difference = np.abs(self.last_mean_reward - np.mean(self.reward_history))

        if difference < 5.0:
            self.learning_rate = self.learning_rate + self.learning_rate * 0.25
            print("Increased learning rate - Difference: {}".format(difference))
        elif difference > 50:
            self.learning_rate = self.learning_rate - self.learning_rate * 0.25
            print("Decreased learning rate - Difference: {}".format(difference))

    def ask(self):
        individuals = []

        number_of_individuals = self.population_size

        if self.configuration.mirrored_sampling:
            # Half the population size, as we add two individuals per sampled noise, when using mirrored_sampling
            number_of_individuals //= 2

        for i in range(number_of_individuals):
            noise_for_individual = self.rng.standard_normal(size=self.individual_size, dtype=np.float32)
            self.noise.append(noise_for_individual)

            # noise_stddev is only used for perturbing the individuals, later, when calculating the new individual,
            # the "original" noise is used, i.e. no multiplication with noise_stddev
            noise_with_stddev = self.configuration.noise_stddev * noise_for_individual

            individuals.append(self.current_individual + noise_with_stddev)

            # Mirrored sampling: Add _and_ subtract the noise to the individual
            if self.configuration.mirrored_sampling:
                individuals.append(self.current_individual - noise_with_stddev)

        return individuals

    def tell(self, rewards):
        # self.reward_history.append(np.mean(rewards))

        # if self.adam.t % 5 == 0:
        #     self.adjust_learning_rate()

        processed_rewards = np.array(rewards, dtype=np.float32)

        if self.configuration.use_centered_ranks:
            processed_rewards = compute_centered_ranks(processed_rewards)

        if self.configuration.mirrored_sampling:
            processed_rewards = processed_rewards[::2] - processed_rewards[1::2]

        g, count = batched_weighted_sum(
            processed_rewards,
            self.noise,
            batch_size=500
        )

        g /= len(rewards)

        assert g.shape == (self.individual_size,) and g.dtype == np.float32 and count == len(self.noise)

        # gradient explanation: -g probably because the Adam implementation does gradient descent, but we want
        # to do gradient ascent since we want to maximize the reward, and the second part of the equation is weight
        # decay
        self.current_individual = self.adam.update(
            theta=self.current_individual,
            gradient=-g + self.configuration.l2_regularization_coefficient * self.current_individual
        )

        self.noise = []
