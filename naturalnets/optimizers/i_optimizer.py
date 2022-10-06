import abc

registered_optimizer_classes = {}


def get_optimizer_class(optimizer_class_name: str):
    if optimizer_class_name in registered_optimizer_classes:
        return registered_optimizer_classes[optimizer_class_name]
    else:
        raise RuntimeError(f"'{optimizer_class_name}' is not a valid optimizer. Please choose one from the following "
                           f"list: {list(registered_optimizer_classes)!r}")


def register_optimizer_class(optimizer_class):
    registered_optimizer_classes[optimizer_class.__name__] = optimizer_class
    return optimizer_class


class IOptimizer(abc.ABC):

    @abc.abstractmethod
    def ask(self):
        pass

    @abc.abstractmethod
    def tell(self, rewards):
        pass
