from time import sleep
from typing import Dict

from flask_microservices.exceptions.port_is_not_available_exception import PortIsNotAvailableException
from flask_microservices.flask_executor.flask_runner import FlaskRunner
from interfaces.microservice_runner_interface import MicroserviceRunnerInterface


class FlaskExecutor(MicroserviceRunnerInterface):
    """
    Class for executing all Flask microservices
    """

    _apps: Dict[int, FlaskRunner]

    def __init__(self):
        self._apps = {}
        self._running = True

    def start(self):
        """
        Start the execution
        """
        while self._running and self._apps:
            sleep(5)

    def stop(self):
        """
        Stop the execution
        """
        self._running = False

    def add_microservice(self, app, port: int, microservice_args, microservice_kwargs):
        """
        Add a new Flask microservice

        :param app: app to add
        :param port: port to add app in
        :param microservice_args: any arguments needed
        :param microservice_kwargs: any dict arguments needed
        """
        if port not in self._apps:
            new_app_process = FlaskRunner(app, port, microservice_args, str(microservice_kwargs))
            new_app_process.run()
            self._apps[port] = new_app_process
        else:
            raise PortIsNotAvailableException(f"The port {port} is not available")

    def stop_microservice(self, port: int):
        """
        Stop a microservice by port

        :param port: port to stop by
        """
        self._apps[port].stop()
        del self._apps[port]
