from abc import ABC, abstractmethod


class ManagerInterface(ABC):
    """
    An interface for managers
    """

    @abstractmethod
    def manage(self, *args, **kwargs):
        """
        Manage by args and/or kwargs
        :param args: arguments for managing
        :param kwargs: kwargs for managing
        """
        pass
