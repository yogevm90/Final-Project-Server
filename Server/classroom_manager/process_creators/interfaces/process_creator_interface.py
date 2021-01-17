from abc import ABC, abstractmethod


class ProcessCreatorInterface(ABC):
    @abstractmethod
    def create_process(self):
        pass

    @abstractmethod
    def stop(self):
        pass
