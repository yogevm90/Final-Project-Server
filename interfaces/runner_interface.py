from abc import ABC, abstractmethod


class RunnerInterface(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass
