import json
from multiprocessing.context import Process
from typing import Dict


from flask_microservices.exceptions.port_is_not_available_exception import PortIsNotAvailableException
from flask_microservices.flask_executor.flask_runner import FlaskRunner
from interfaces.microservice_runner_interface import MicroserviceRunnerInterface


class FlaskExecutor(MicroserviceRunnerInterface):
    _apps: Dict[int, FlaskRunner]

    def __init__(self):
        self._apps = {}

    def start(self):
        while True:
            pass

    def add_microservice(self, app, port: int, microservice_args, microservice_kwargs):
        if port not in self._apps:
            new_app_process = FlaskRunner(app, port, microservice_args, str(microservice_kwargs))
            new_app_process.run()
            self._apps[port] = new_app_process
        else:
            raise PortIsNotAvailableException(f"The port {port} is not available")

    def stop_microservice(self, port: int):
        self._apps[port].stop()
        del self._apps[port]
