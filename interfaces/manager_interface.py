from abc import ABC, abstractmethod


class ManagerInterface(ABC):
    @abstractmethod
    def manage(self, *args, **kwargs):
        pass
