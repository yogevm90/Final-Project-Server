from abc import ABC, abstractmethod


class CleanerInterface(ABC):
    @abstractmethod
    def start_clean(self):
        pass

    @abstractmethod
    def stop_clean(self):
        pass
