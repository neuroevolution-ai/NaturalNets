import abc

from optimizer.canonical_es import OptimizerCanonicalEs
from optimizer.cma_es_deap import OptimizerCmaEsDeap
from optimizer.cma_es_pycma import OptimizerCmaEsPycma
from optimizer.openai_es import OptimizerOpenAIES

# TODO: Do this registration via class decorators
registered_optimizer_classes = {'CMA-ES-Deap': OptimizerCmaEsDeap,
                                'CMA-ES-Pycma': OptimizerCmaEsPycma,
                                'Canonical-ES': OptimizerCanonicalEs,
                                'OpenAI-ES': OptimizerOpenAIES}


class IOptimizer(abc.ABC):

    @abc.abstractmethod
    def ask(self):
        pass

    @abc.abstractmethod
    def tell(self, rewards):
        pass
