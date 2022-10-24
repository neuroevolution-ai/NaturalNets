from naturalnets.optimizers.i_optimizer import IOptimizer
from naturalnets.optimizers import OptimizerCmaEsDeapCfg


class DummyOptimizer(IOptimizer):

    def __init__(self, configuration: dict):
        try:
            self.config = OptimizerCmaEsDeapCfg(**configuration)
        except TypeError:
            raise RuntimeError(f"Using the RandomBrain (i.e. the monkey tester) requires using the "
                               "'CmaEsDeap' optimizer.")

        self.population_size = self.config.population_size

    def ask(self):
        # Run as many runs with the monkey tester, as with a normal brain. Therefore, simulate a full population
        # by using empty lists as the genome (they are not used by the brain, because the individual size is 0)
        return [[] for _ in range(self.population_size)]

    def tell(self, rewards):
        pass
