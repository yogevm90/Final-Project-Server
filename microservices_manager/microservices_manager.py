import json
import os
from typing import Dict

from interfaces.manager_interface import ManagerInterface
from interfaces.microservice_runner_interface import MicroserviceRunnerInterface
from utilities.custom_importer.custom_importer import CustomImporter


class MicroservicesManager(ManagerInterface):
    _apps_config_file_path: str
    _apps_config_file_content: Dict
    _executor: MicroserviceRunnerInterface

    def __init__(self):
        self._apps_config_file_path = os.path.join(os.path.dirname(__file__), "configurations", "default.json")
        self._apps_config_file_content = {}
        self._executor = None

    def manage(self, apps_config_file_path: str = "", apps_to_execute: Dict = None):
        if apps_config_file_path:
            self._apps_config_file_path = apps_config_file_path

        with open(self._apps_config_file_path, "r") as apps_config_file_file:
            self._apps_config_file_content = json.load(apps_config_file_file)

        if apps_to_execute is None:
            apps_to_execute = self._apps_config_file_content["apps"]

        self._executor = CustomImporter.import_object(self._apps_config_file_content["executor"])()
        self._start_execution(apps_to_execute)

    def _start_execution(self, apps_to_execute: Dict):
        for app in apps_to_execute.values():
            self._executor.add_microservice(app=app,
                                            port=app["port"],
                                            microservice_args=app["args"],
                                            microservice_kwargs=app["kwargs"])
        self._executor.start()
