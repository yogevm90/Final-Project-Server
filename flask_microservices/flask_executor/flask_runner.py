import os
import subprocess
import sys
from typing import Dict

from interfaces.runner_interface import RunnerInterface


class FlaskRunner(RunnerInterface):
    """
    A class for executing a microservice app
    """

    _app: Dict
    _flask_app_base: str
    _port: int
    _python_executable: str
    _process: subprocess.Popen

    def __init__(self, app: Dict, port: int, microservice_args, microservice_kwargs):
        """
        :param app: Flask app
        :param port: port to run in
        :param microservice_args: any arguments needed
        :param microservice_kwargs: any dict arguments needed
        """
        self._app = app
        self._kwargs = microservice_kwargs
        self._args = microservice_args
        self._flask_app_base = os.path.join(os.path.dirname(__file__), "flask_app_base.py")
        self._port = port
        self._python_executable = sys.executable
        self._process = None

    def run(self):
        """
        Run the microservice
        """
        cmd = f"\"{self._python_executable}\" \"{self._flask_app_base}\" " \
              f"-a {self._app['module']} " \
              f"-p {self._port} " \
              f"-n {self._app['name']}"
        if self._kwargs != "{}":
            cmd += f" -k \"{self._kwargs}\""
        if self._args:
            cmd += f"-r {' '.join(self._args)}"
        process = subprocess.Popen(cmd,
                                   shell=True,
                                   cwd=os.getcwd())
        self._process = process

    def stop(self):
        """
        Stop the microservice
        """
        self._process.terminate()
