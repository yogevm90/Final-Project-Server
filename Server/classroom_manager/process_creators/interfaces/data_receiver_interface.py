from abc import ABC, abstractmethod


class DataReceiverInterface(ABC):
    @abstractmethod
    def receive_data(self):
        pass
