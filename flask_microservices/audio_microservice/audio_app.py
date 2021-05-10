import io
import copy
import os
from multiprocessing import Lock
from pathlib import Path

import flask
from flask_compress import Compress
from flask_cors import CORS, cross_origin

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from utilities.logging.scholapp_server_logger import ScholappLogger


class AudioApp(FlaskAppBase):
    """
    A class for a microservice to save images
    """

    def __init__(self, import_name="AudioApp", **kwargs):
        """
        :param import_name: import name
        :param kwargs: any dict arguments needed
        """
        super().__init__(import_name, **kwargs)
        super()._chdir(__file__)
        ScholappLogger.info(f"Setting up {import_name}")
        CORS(self, resources={r"/GetImage": {"origins": "*"}})
        self._audios = {}
        self._compress = Compress()
        self._compress.init_app(self)
        self._static_folder = Path(os.path.dirname(__file__)) / "static"
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        """
        Setup REST API routes
        """

        @self.route("/GetAudioPath", methods=["POST"])
        @self._compress.compressed()
        def get_audio_path():
            login_details = flask.request.get_json()
            user_p = self._static_folder / login_details["username"]
            if not user_p.is_dir():
                user_p.mkdir()
            self._audios[login_details["username"]] = user_p
            return flask.Response(str(user_p))
