from abc import ABC, abstractmethod


class CreatorInterface(ABC):
    """
    An interface for creators
    """

    @abstractmethod
    def create(self, *args, **kwargs):
        """
        Create something from args or/and kwargs
        :param args: arguments for creation
        :param kwargs: kwargs for creation
        :return: created object
        """
        pass
