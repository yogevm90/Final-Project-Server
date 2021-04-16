import os
from pathlib import Path

import flask
from flask_cors import CORS

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from utilities.logging.scholapp_server_logger import ScholappLogger

DEFAULT = "default"


class ImageApp(FlaskAppBase):
    """
    A class for a microservice to save images
    """

    def __init__(self, import_name="ImageApp", **kwargs):
        """
        :param import_name: import name
        :param kwargs: any dict arguments needed
        """
        super().__init__(import_name, **kwargs)
        super()._chdir(__file__)
        self._img_counter = 1
        ScholappLogger.info(f"Setting up {import_name}")
        CORS(self, resources={r"/UploadImage": {"origins": "*"}})
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        """
        Setup REST API routes
        """
        static_files = [p.stem for p in Path("static").iterdir() if p.stem != DEFAULT]
        if static_files:
            static_files.sort()
            self._img_counter = int(static_files[-1])

        @self.route("/UploadImage", methods=["POST", "PUT"])
        def save_img():
            """
            Save an image
            :return: json for the path that the image was saved to
            """
            return self._save_img(flask.request.data)

    @property
    def ImgCounter(self) -> int:
        """
        :return: Number of images saved
        """
        return self._img_counter

    def _save_img(self, img_data):
        img_path = os.path.join("static", f"{self._img_counter}.png")
        with open(img_path, "wb") as img_f:
            img_f.write(img_data)

        return flask.jsonify({"img_path": img_path})
