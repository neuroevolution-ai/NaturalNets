import warnings
from typing import Union, List, Tuple

import numpy as np
import torch
from attrs import define, field, validators
from evotorch import Problem
from evotorch.algorithms import CMAES

from naturalnets.optimizers.i_optimizer import IOptimizer, IOptimizerCfg, register_optimizer_class


def convert_device(device_name: str) -> str:
    if device_name == "gpu":
        return "cuda"
    return device_name


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerCmaEsEvoTorchCfg(IOptimizerCfg):
    # population_size must be >= 2, otherwise an internal matrix factorization is not possible
    population_size: int = field(validator=[validators.instance_of(int), validators.ge(2)])
    sigma: Union[int, float] = field(validator=[validators.instance_of((int, float))])

    # Defines the upper and lower bound for the first population
    initial_bounds: Tuple[int] = field(default=(-1, 1), converter=tuple)

    # See the parameter description in the __init__() function here:
    # https://docs.evotorch.ai/v0.4.0/reference/evotorch/#evotorch.algorithms.cmaes.CMAES
    limit_C_decomposition: bool = field(default=False, validator=validators.instance_of(bool))

    # Can be "cpu" or "gpu"
    device: str = field(default="cpu", converter=convert_device,
                        validator=[validators.instance_of(str), validators.in_(["cpu", "cuda"])])

    @population_size.validator
    def validate_limit_c_decomposition(self, attribute, value):
        if self.limit_C_decomposition and value < 75:
            warnings.warn(f"'limit_C_decomposition' is True and the 'population_size' is lower than 75, this may cause "
                          "a division by zero! Try increasing the 'population_size'.")

    @initial_bounds.validator
    def validate_initial_bounds(self, attribute, value):
        if len(value) != 2:
            raise ValueError(f"'initial_bounds' must be a list of two integers, but it contains {len(value)} values.")

        if not all(isinstance(x, int) or isinstance(x, float) for x in value):
            raise ValueError(f"All values in 'initial_bounds' must be integers or floats. You provided: '{value}'.")

        if value[0] >= value[1]:
            raise ValueError(f"The first value of 'initial_bounds' must be smaller than the second value. "
                             f"You provided: '{value}'.")

    @device.validator
    def validate_gpu_availability(self, attribute, value):
        if value == "cuda":
            if not torch.cuda.is_available():
                raise ValueError(f"Torch could not detect CUDA, but you set 'device' to '{value}' or 'gpu'. "
                                 "Try using the CPU by setting 'device' to 'cpu'.")

            try:
                torch.cuda.get_device_name(value)
            except AssertionError:
                raise ValueError(f"PyTorch cannot detect a GPU on this machine. The CUDA "
                                 f"device count is: {torch.cuda.device_count()}. Try fixing PyTorch + CUDA or use the "
                                 "CPU by setting 'device' to 'cpu'.")


@register_optimizer_class
class CmaEsEvoTorch(IOptimizer):

    def __init__(self, individual_size: int, global_seed: int, configuration: dict, **kwargs):
        super().__init__(individual_size, global_seed, configuration, **kwargs)

        config = OptimizerCmaEsEvoTorchCfg(**self.config_dict)

        problem = Problem("max", self.assign_reward_to_evotorch, solution_length=individual_size,
                          initial_bounds=config.initial_bounds, device=config.device)

        try:
            self.cma_es = CMAES(problem, stdev_init=config.sigma, popsize=config.population_size,
                                limit_C_decomposition=config.limit_C_decomposition)
        except ValueError:
            raise ValueError("The creation of CMA-ES failed, probably due to a division by zero. If that is the "
                             "case, try increasing the 'population_size' and/or 'sigma', or disable "
                             "'limit_C_decomposition'.")

        self.population = None

        self.i = 0
        self.rewards = None

    def assign_reward_to_evotorch(self, _) -> torch.Tensor:
        """
        Normally this function would evaluate a genome given by EvoTorch by calculating its reward. However we have
        another pipeline, so we abuse this function to simply return the reward that we calculated before.
        """
        rew = self.rewards[self.i]
        self.i += 1

        return rew

    def ask(self) -> List[np.ndarray]:
        self.population = self.cma_es.population.values.cpu().numpy()

        return self.population

    def tell(self, rewards: List[float]) -> np.ndarray:
        # These will be used in the CMA-ES step by EvoTorch in the assign_reward_to_evotorch() function
        self.rewards = rewards
        self.i = 0

        best_genome_current_generation = self.population[np.argmax(rewards)]

        self.cma_es.step()

        return best_genome_current_generation
