import os
from threading import Lock
from typing import Dict

import flask
from flask_compress import Compress
from flask_cors import CORS, cross_origin

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from utilities.logging.scholapp_server_logger import ScholappLogger


class ImagesContainer(object):
    _images: dict
    _counters: dict
    _deleting: Dict[str, Lock]

    def __init__(self):
        self._images = {}
        self._counters = {}
        self._deleting = {}

    def get_image(self, user):
        if user in self._images and len(self._images[user]) > 0:
            # Making sure we are not deleting right now
            if self._deleting[user].locked():
                self._deleting[user].acquire()
                self._deleting[user].release()
            return self._images[user][-1]
        return None

    def add_image(self, image, user):
        if user not in self._images:
            self._images[user] = []
            self._counters[user] = 0
            self._deleting[user] = Lock()
        # Let some images get garbage collected - at most we can have 1000 at the same time
        if self._counters[user] - 500 >= 500:
            self._counters[user] -= 500
            ScholappLogger.info(f"Deleting images for {user}")
            self._deleting[user].acquire()
            self._images[user] = self._images[user][500:]
            self._deleting[user].release()
        self._counters[user] += 1
        self._images[user] += [image]


class VideoApp(FlaskAppBase):
    """
    A class for a microservice to save images
    """

    def __init__(self, import_name="VideoApp", is_screen_share="false", **kwargs):
        """
        :param import_name: import name
        :param kwargs: any dict arguments needed
        """
        super().__init__(import_name, **kwargs)
        super()._chdir(__file__)
        self._img_counter = 1
        ScholappLogger.info(f"Setting up {import_name}")
        CORS(self, resources={r"/GetImage": {"origins": "*"}})
        self._images = ImagesContainer()
        self._compress = Compress()
        self._compress.init_app(self)

        if is_screen_share == "false":
            default_img_path = os.path.join("static", "default.jpg")
        else:
            default_img_path = os.path.join("static", "default_screen.jpg")

        with open(default_img_path, "rb") as default_img:
            self._default_img = default_img.read()
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        """
        Setup REST API routes
        """

        @self.route("/GetImage/<user>")
        @cross_origin()
        @self._compress.compressed()
        def get_img(user):
            image = self._images.get_image(user)
            if image:
                ScholappLogger.info("Got Video")
                return flask.Response(image, mimetype="image/jpg")
            else:
                ScholappLogger.info("Sending default")
                return flask.Response(self._default_img, mimetype="image/jpg")

        @self.route("/UploadImage/<user>", methods=["POST"])
        @self._compress.compressed()
        def upload_img(user):
            self._images.add_image(flask.request.data, user)
            return flask.jsonify({"verdict": True})
