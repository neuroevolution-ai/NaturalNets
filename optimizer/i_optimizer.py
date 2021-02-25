import abc


class IOptimizer(abc.ABC):

    @abc.abstractmethod
    def ask(self):
        pass

    @abc.abstractmethod
    def tell(self, rewards):
        pass
