from abc import ABC, abstractmethod


class QueryListenerInterface(ABC):
    @abstractmethod
    def start_listening(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop_listening(self, *args, **kwargs):
        pass
