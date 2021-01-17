from abc import ABC, abstractmethod


class ProcessManagerInterface(ABC):
    @staticmethod
    @abstractmethod
    def initialize(data):
        pass

    @staticmethod
    @abstractmethod
    def manage(data):
        pass
