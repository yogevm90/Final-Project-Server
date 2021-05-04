import os
from copy import deepcopy
from pathlib import Path
from threading import Lock

import flask
from flask_cors import CORS, cross_origin

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from utilities.logging.scholapp_server_logger import ScholappLogger


class ImagesContainer(object):
    def __init__(self):
        self._images = {}

    def get_image(self, user):
        if user in self._images and len(self._images[user]) > 0:
            img_copy = deepcopy(self._images[user][0])
            return img_copy

    def add_image(self, image, user):
        if user not in self._images:
            self._images[user] = []
        self._images[user] += [image]


class VideoApp(FlaskAppBase):
    """
    A class for a microservice to save images
    """

    def __init__(self, import_name="VideoApp", **kwargs):
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
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        """
        Setup REST API routes
        """

        @self.route("/GetImage/<user>")
        @cross_origin()
        def get_img(user):
            image = self._images.get_image(user)
            if image:
                return flask.Response(self._images.get_image(user), mimetype="image/jpg")
            else:
                return flask.redirect("/static/default.jpg")

        @self.route("/UploadImage/<user>", methods=["POST"])
        def upload_img(user):
            self._images.add_image(flask.request.data, user)
            return flask.jsonify({"verdict": True})
