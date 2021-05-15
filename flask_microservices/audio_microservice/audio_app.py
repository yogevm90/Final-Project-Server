import os
import shutil
import time
import traceback
from pathlib import Path
from threading import Thread

import flask
from flask_compress import Compress
from flask_cors import CORS

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from utilities.logging.scholapp_server_logger import ScholappLogger


class Running(object):
    def __init__(self):
        self.running = True


def clean_file(file: Path, running: Running):
    start = time.time()
    times_failed = 0
    while (time.time() - start) < 100 and running.running:
        passed = time.time() - start
        ScholappLogger.info(f"Passed in seconds: {passed}")
        try:
            file.unlink()
            ScholappLogger.info(f"Is deleted: {file.is_file()}")
        except Exception:
            times_failed += 1
            pass
        time.sleep(1)

    ScholappLogger.info(f"Is deleted: {file.is_file()}")


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
        self._cleaner_threads = {}
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
                    to_del = self._audios[class_id][username] / "record.wav"
                    if to_del.is_file():
                        ScholappLogger.info(f"Deleting path for audio: {to_del}")
                        # to_del.unlink()
                        os.remove(str(to_del))
                        ScholappLogger.info(f"Deleted: {to_del.is_file()}")
                        running = Running()
                        thread = Thread(target=clean_file, args=(to_del, running))
                        thread.run()
                        self._cleaner_threads[username] = {"thread": thread, "running": running}
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

            if username in self._cleaner_threads:
                self._cleaner_threads[username]["running"].running = False
                self._cleaner_threads[username]["thread"].join()

            class_p = self._static_folder / class_id
            user_p = class_p / username
            ScholappLogger.info(f"Creating path for audio: {class_p}")
            ScholappLogger.info(f"Creating path for audio: {user_p}")
            try:
                class_p.mkdir(exist_ok=True)
            except FileExistsError:
                pass
            try:
                user_p.mkdir(exist_ok=True)
            except FileExistsError:
                pass

            ScholappLogger.info(f"Created {class_p}: {class_p.is_dir()}")
            ScholappLogger.info(f"Created {user_p}: {user_p.is_dir()}")

            if class_id not in self._audios:
                self._audios[class_id] = {}
            self._audios[class_id][username] = user_p
            return flask.make_response(str(user_p))

        # @self.route("/PostAudio/<user>", methods=["POST"])
        # @self._compress.compressed()
        # def post_audio(user):
        #     audio = flask.request.get_data()
        #     self._audios[user] = audio
        #     return flask.make_response()
        #
        # @self.route("/GetAudio/<user>")
        # @self._compress.compressed()
        # def post_audio(user):
        #     return flask.Response(self._audios[user], mimetype="audio/wav")
