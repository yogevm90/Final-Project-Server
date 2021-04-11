import argparse
import json
import os
from abc import ABC, abstractmethod

from flask import Flask

from utilities.custom_importer.custom_importer import CustomImporter
from utilities.logging.scholapp_server_logger import ScholappLogger


class FlaskAppBase(Flask, ABC):
    def __init__(self, import_name, logs_name, *args, **kwargs):
        ScholappLogger.init_logger(logs_name)
        super().__init__(import_name, *args, **kwargs)

    @abstractmethod
    def _setup(self, *args, **kwargs):
        pass

    @staticmethod
    def _chdir(file):
        root_path = os.path.dirname(file)
        os.chdir(root_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--flask_app",
                        type=str,
                        required=True,
                        help="App to execute")
    parser.add_argument("-p", "--port",
                        type=int,
                        required=True,
                        help="Port to execute on")
    parser.add_argument("-n", "--import_name",
                        type=str,
                        required=True,
                        help="Import name for the app")
    parser.add_argument("-r", "--microservices_args",
                        nargs="+",
                        default=[],
                        help="Import name for the app")
    parser.add_argument("-k", "--microservices_kwargs",
                        type=str,
                        default="{}",
                        help="Import name for the app")
    args = parser.parse_args()
    app_import = CustomImporter.import_object({"name": args.import_name, "module": args.flask_app})
    kwargs = json.loads(args.microservices_kwargs.replace("'", "\""))
    if args.microservices_args:
        app = app_import(import_name=args.flask_app, *args.microservices_args, **kwargs)
    else:
        app = app_import(import_name=args.flask_app, **kwargs)

    app.run(host="127.0.0.1", port=args.port)
