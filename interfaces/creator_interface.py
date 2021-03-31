from abc import ABC, abstractmethod


class CreatorInterface(ABC):
    @abstractmethod
    def create(self, *args, **kwargs):
        pass
