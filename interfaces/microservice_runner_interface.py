from abc import ABC, abstractmethod


class MicroserviceRunnerInterface(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def add_microservice(self, app, port: int, microservice_args, microservice_kwargs):
        pass

    @abstractmethod
    def stop_microservice(self, port: int):
        pass
