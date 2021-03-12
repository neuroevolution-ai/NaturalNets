import abc


class IBrain(abc.ABC):

    @abc.abstractmethod
    def step(self, u):
        pass

    @abc.abstractmethod
    def reset(self):
        pass
