import os

import flask
from flask_compress import Compress
from flask_cors import CORS, cross_origin

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from utilities.logging.scholapp_server_logger import ScholappLogger


class AudioContainer(object):
    def __init__(self):
        self._audios = {}

    def get_audio(self, user):
        if user in self._audios and len(self._audios[user]) > 0:
            return self._audios[user][-1]
        return None

    def add_audio(self, audio, user):
        if user not in self._audios:
            self._audios[user] = []
        self._audios[user] += [audio]


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
        self._img_counter = 1
        ScholappLogger.info(f"Setting up {import_name}")
        CORS(self, resources={r"/GetImage": {"origins": "*"}})
        self._audios = AudioContainer()
        self._compress = Compress()
        self._compress.init_app(self)
        default_img_path = os.path.join("static", "default.jpg")
        with open(default_img_path, "rb") as default_img:
            self._default_img = default_img.read()
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        """
        Setup REST API routes
        """

        @self.route("/GetAudio/<user>", methods=["POST"])
        @cross_origin()
        @self._compress.compressed()
        def get_audio(user):
            image = self._audios.get_audio(user)
            if image:
                return flask.Response(image, mimetype="audio/wav")
            else:
                return flask.jsonify({"verdict": False}), 500

        @self.route("/UploadAudio/<user>", methods=["POST"])
        @self._compress.compressed()
        def upload_audio(user):
            self._audios.add_audio(flask.request.data, user)
            return flask.jsonify({"verdict": True})
