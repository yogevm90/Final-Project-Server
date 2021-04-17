from abc import ABC, abstractmethod


class Serializable(ABC):
    """
    An interface for all serializable objects
    """

    @abstractmethod
    def serialize(self):
        """
        Serialize object
        """
        pass

    @abstractmethod
    def deserialize(self):
        """
        Deserialize object
        """
        pass
