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

import attr
import numpy as np
from optimizers.i_optimizer import IOptimizer, registered_optimizer_classes


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerOpenAIESCfg:
    type: str
    population_size: int
    learning_rate: np.float32
    l2coeff: np.float32
    noise_stdev: np.float32
    use_centered_ranks: bool = True


class Adam:
    def __init__(self, num_params, stepsize, beta1=0.9, beta2=0.999, epsilon=1e-08):
        self.dim = num_params
        self.t = 0

        self.stepsize = stepsize
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m = np.zeros(self.dim, dtype=np.float32)
        self.v = np.zeros(self.dim, dtype=np.float32)

    def update(self, theta, gradient):
        self.t += 1
        step = self._compute_step(gradient)
        # ratio = np.linalg.norm(step) / np.linalg.norm(theta)
        theta_new = theta + step
        return theta_new  # , ratio

    def _compute_step(self, gradient):
        a = self.stepsize * np.sqrt(1 - self.beta2 ** self.t) / (1 - self.beta1 ** self.t)
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradient
        self.v = self.beta2 * self.v + (1 - self.beta2) * (gradient * gradient)
        step = -a * self.m / (np.sqrt(self.v) + self.epsilon)
        return step


class OptimizerOpenAIES(IOptimizer):
    def __init__(self, individual_size: int, configuration: dict):
        self.noise = []
        self.random_state = np.random.RandomState(seed=0)
        self.individual_size = individual_size
        self.configuration = OptimizerOpenAIESCfg(**configuration)
        self.current_individual = self.initialize_individual(std=0.01)

        self.population_size = self.configuration.population_size
        self.learning_rate = self.configuration.learning_rate
        self.adam = Adam(num_params=self.individual_size, stepsize=self.learning_rate)

    def initialize_individual(self, std=1.0):
        """
        This initializes the individual when first starting the optimizers. OpenAI used this in their implementation
        and Experiments showed that this could be a factor for the performance of the algorithm.

        Source: https://github.com/openai/evolution-strategies-starter

        :param std:
        :return:
        """
        out = np.random.randn(self.individual_size).astype(np.float32)
        out *= std / np.sqrt(np.square(out).sum(axis=0, keepdims=True))

        return out

    def compute_ranks(self, x):
        """
        Returns ranks in [0, len(x))
        Note: This is different from scipy.stats.rankdata, which returns ranks in [1, len(x)].
        """
        assert x.ndim == 1
        ranks = np.empty(len(x), dtype=int)
        ranks[x.argsort()] = np.arange(len(x))
        return ranks

    def compute_centered_ranks(self, x):
        y = self.compute_ranks(x.ravel()).reshape(x.shape).astype(np.float32)
        y /= (x.size - 1)
        y -= .5
        return y

    def ask(self):
        individuals = []
        for i in range(self.population_size):
            noise_for_individual = self.random_state.randn(self.individual_size)
            noisy_individual = self.current_individual + noise_for_individual

            self.noise.append(noise_for_individual)
            individuals.append(noisy_individual)

        return individuals

    def tell(self, rewards):
        if self.configuration.use_centered_ranks:
            rewards = self.compute_centered_ranks(np.array(rewards, dtype=np.float32))

        # TODO maybe improve the calculation using numpy function
        weighted_noise = np.sum([n * r for (n, r) in zip(self.noise, rewards)], axis=0, dtype=np.float32)

        weighted_noise /= len(weighted_noise)

        gradient = -weighted_noise + self.configuration.l2coeff * self.current_individual
        self.current_individual = self.adam.update(self.current_individual, gradient=gradient)

        self.noise = []


# TODO: Do this registration via class decorator
registered_optimizer_classes["OpenAI-ES"] = OptimizerOpenAIES


