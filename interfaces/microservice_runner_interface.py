from abc import ABC, abstractmethod
from typing import Dict


class MicroserviceRunnerInterface(ABC):
    """
    An interface for microservice runners
    """

    @abstractmethod
    def start(self):
        """
        Start microservice runner
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop microservice runner
        """
        pass

    @abstractmethod
    def add_microservice(self, app: Dict, port: int, microservice_args: tuple, microservice_kwargs: Dict):
        """
        Add microservice to run

        :param app: microservice to add
        :param port: port to start microservice on
        :param microservice_args: arguments for starting the app
        :param microservice_kwargs: kwargs for starting the app
        """
        pass

    @abstractmethod
    def stop_microservice(self, port: int):
        """
        Stop a microservice on a specific port

        :param port: port to stop
        """
        pass
