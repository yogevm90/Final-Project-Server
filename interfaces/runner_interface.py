from abc import ABC, abstractmethod


class RunnerInterface(ABC):
    """
    An interface for runners
    """

    @abstractmethod
    def run(self):
        """
        Start running
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop running
        """
        pass
