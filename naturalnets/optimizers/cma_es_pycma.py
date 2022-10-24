import attr
import cma

from naturalnets.optimizers.i_optimizer import IOptimizer, register_optimizer_class


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class OptimizerCmaEsPycmaCfg:
    type: str
    sigma: float = 1.0


@register_optimizer_class
class CmaEsPyCma(IOptimizer):

    def __init__(self, individual_size: int, configuration: dict):

        self.individual_size = individual_size
        config = OptimizerCmaEsPycmaCfg(**configuration)

        self.es = cma.CMAEvolutionStrategy(x0=[0.0] * individual_size, sigma0=config.sigma)

        self.solutions = None

    def ask(self):
        self.solutions = self.es.ask()
        return self.solutions

    def tell(self, rewards):
        self.es.tell(self.solutions, rewards)
