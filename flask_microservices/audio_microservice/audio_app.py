import os
import shutil
import traceback
from pathlib import Path

import flask
from flask_compress import Compress
from flask_cors import CORS

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
        if not self._static_folder.is_dir():
            self._static_folder.mkdir()
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        """
        Setup REST API routes
        """

        @self.route("/DeleteAudioPath", methods=["POST"])
        @self._compress.compressed()
        def del_audio_path():
            try:
                login_details = flask.request.get_json()
                class_id = login_details["class_id"]
                username = login_details["username"]
                if class_id in self._audios and username in self._audios[class_id]:
                    if self._audios[class_id][username].is_dir():
                        ScholappLogger.info(f"Deleting path for audio: {self._audios[class_id][username]}")
                        shutil.rmtree(str(self._audios[class_id][username]))
                        self._audios[class_id][username].rmdir()
                return flask.jsonify({"verdict": True})
            except Exception:
                ScholappLogger.error(traceback.format_exc())
                return flask.jsonify({"verdict": False})

        @self.route("/GetAudioPath", methods=["POST"])
        @self._compress.compressed()
        def get_audio_path():
            login_details = flask.request.get_json()
            class_id = login_details["class_id"]
            username = login_details["username"]

            user_p = self._static_folder / class_id / username
            ScholappLogger.info(f"Creating path for audio: {user_p}")
            user_p.mkdir(parents=True, exist_ok=True)

            if class_id not in self._audios:
                self._audios[class_id] = {}
            self._audios[class_id][username] = user_p
            return flask.make_response(str(user_p))
