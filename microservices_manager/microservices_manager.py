import json
import os
from typing import Dict, List, Tuple

from interfaces.manager_interface import ManagerInterface
from interfaces.microservice_runner_interface import MicroserviceRunnerInterface
from utilities.custom_importer.custom_importer import CustomImporter
from utilities.logging.scholapp_server_logger import ScholappLogger


class MicroservicesManager(ManagerInterface):
    """
    A class for managing all microservices and starting them by a JSON configuration file
    """

    _apps_config_file_path: str
    _apps_config_file_content: Dict
    _executor: MicroserviceRunnerInterface

    def __init__(self):
        self._logs_path = ScholappLogger.init_logger("MicroservicesManager_logs.txt", create_time_folder=True)
        self._apps_config_file_path = os.path.join(os.path.dirname(__file__), "configurations", "default1.json")
        self._apps_config_file_content = {}
        self._executor = None
        self._envs = {
            "_logs_path": {
                "val": self._logs_path,
                "type": "path"
            }
        }

    def manage(self, apps_config_file_path: str = "", apps_to_execute: Dict = None):
        """
        Start managing all microservices

        :param apps_config_file_path: configuration file to start management by
        :param apps_to_execute: dictionary for apps to execute
        """
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
            app["args"] = self._set_envs_args(app["args"])
            app["kwargs"] = self._set_envs_kwargs(app["kwargs"])
            self._executor.add_microservice(app=app,
                                            port=app["port"],
                                            microservice_args=app["args"],
                                            microservice_kwargs=app["kwargs"])
        self._executor.start()

    def _set_envs_args(self, args_from_f: List[str]):
        result = []
        for arg in args_from_f:
            result += [self._get_new_arg(arg)]

        return result

    def _set_envs_kwargs(self, kwargs_from_f: Dict[str, str]):
        result = {}
        for key, arg in kwargs_from_f.items():
            result[key] = self._get_new_arg(arg)

        return result

    def _get_new_arg(self, arg: str):
        result = []
        for env_name, val in self._envs.items():
            if "${%s}" % env_name in arg:
                result += [(env_name, val)]

        for env in result:
            arg = MicroservicesManager._replace_env(arg, env)
        return arg

    @staticmethod
    def _replace_env(arg: str, env: Tuple[str, Dict]):
        if env[1]["type"] == "path":
            arg = arg.split("${%s}" % env[0])[-1]
            arg = arg.replace("/", "").replace("\\", "")
            arg = os.path.join(env[1]["val"], arg)
        else:
            arg = arg.replace("${%s}" % env, str(env[1]["val"]))
        return arg


