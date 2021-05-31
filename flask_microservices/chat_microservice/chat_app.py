import os
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, List

import flask
import requests
from flask_cors import CORS, cross_origin
from pyomo.solvers.tests.checks.test_CPLEXDirect import TestAddCon

from flask_microservices.chat_microservice.teacher_chat_session import TeacherChatSession
from server.interfaces.jsonable import Jsonable
from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from utilities.logging.scholapp_server_logger import ScholappLogger
from utilities.server_login.server_login import ServerLogin

DEFAULT = "default"
TEACHER_COOKIE_KEY = "scholappteacher"
STUDENT_COOKIE_KEY = "scholappstudent"


class Message(Jsonable):
    def __init__(self):
        pass

    def json(self):
        pass


class ChatApp(FlaskAppBase):
    _teachers_sessions: Dict[str, TeacherChatSession]

    """
    A class for a microservice to save images
    """

    def __init__(self, import_name="ChatApp", **kwargs):
        """
        :param import_name: import name
        :param kwargs: any dict arguments needed
        """
        super().__init__(import_name, **kwargs)
        super()._chdir(__file__)
        ScholappLogger.info(f"Setting up {import_name}")
        self._teachers_sessions = {}

        CORS(self, resources={
            r"/TeacherOpenSession": {"origins": "*"},
            r"/StudentOpenSession": {"origins": "*"},
            r"/TeacherSendResponse": {"origins": "*"},
            r"/StudentSendResponse": {"origins": "*"},
            r"/TeacherGetMessages": {"origins": "*"},
            r"/TeacherHasNewMessages": {"origins": "*"},
            r"/StudentGetMessages": {"origins": "*"},
        })
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        """
        Setup REST API routes
        """

        @self.route("/TeacherOpenSession", methods=["POST"])
        def open_teacher_session():
            return self.actual_open_session(is_teacher=True)

        @self.route("/StudentOpenSession", methods=["POST"])
        def open_student_session():
            return self.actual_open_session()

        @self.route("/TeacherSendResponse", methods=["POST"])
        def teacher_send_response():
            return self.actual_send_response(is_teacher=True)

        @self.route("/StudentSendResponse", methods=["POST"])
        def student_send_response():
            return self.actual_send_response()

        @self.route("/TeacherGetMessages", methods=["POST"])
        def teacher_get_messages():
            return self.actual_get_response(is_teacher=True)

        @self.route("/TeacherHasNewMessages", methods=["POST"])
        def teacher_has_messages():
            return self.actual_has_response()

        @self.route("/StudentGetMessages", methods=["POST"])
        def student_get_messages():
            return self.actual_get_response()

    @staticmethod
    def _verify_login_details(username, password, is_teacher=False):
        return ServerLogin.login(username, password, is_teacher)

    @staticmethod
    def _test_is_verified(username, test_id):
        response = requests.get(f"http://127.0.0.1:5000/GetUserIsVerified/{test_id}/{username}")
        return response.json()["verified"]

    def actual_open_session(self, is_teacher=False):
        json_data = flask.request.get_json()
        ScholappLogger.info(f"Json data is: {json_data}")

        logged_in = ChatApp._verify_login_details(username=json_data["username"], password=json_data["password"],
                                                  is_teacher=is_teacher)

        if not logged_in:
            return flask.jsonify({"status": "Username and Password verification failed!"})

        cookie = str(uuid.uuid3(uuid.NAMESPACE_DNS, json_data["username"] + json_data["password"] + str(uuid.uuid4())))

        if is_teacher:
            username = json_data["username"]
            ScholappLogger.info(f"Teacher session opened: {username}")
            self._teachers_sessions[username] = TeacherChatSession(username,
                                                                   json_data["participants"],
                                                                   cookie)
        else:
            user = json_data["username"]
            if not ChatApp._test_is_verified(user, json_data["test_id"]):
                ScholappLogger.info(f"Test is not verified")
                return flask.jsonify({"status": "You didn't verify yourself by phone!"})
            if json_data["teacher"] in self._teachers_sessions:
                ScholappLogger.info(f"Adding user {user}")
                student_exists = self._teachers_sessions[json_data["teacher"]].add_student(user, cookie)
                if not student_exists:
                    return flask.make_response("Failure"), 500

        resp = {"status": "success", "cookie": cookie}

        return flask.jsonify(resp)

    def actual_send_response(self, is_teacher=False):
        json_data = flask.request.get_json()
        ScholappLogger.info(f"Json data is: {json_data}")

        if "time" not in json_data:
            now = datetime.now()
            json_data["time"] = now.strftime("Date: %d/%m/%Y Time: %H:%M:%S.%f")

        if is_teacher:
            if json_data["username"] in self._teachers_sessions:
                teacher_session = self._teachers_sessions[json_data["username"]]
                msg = json_data["msg"]
                ScholappLogger.info(f"--- msg : {msg} ---")

                return teacher_session.add_teacher_msg(msg, json_data["student"], json_data["cookie"],
                                                       json_data["time"])
            else:
                return flask.make_response("FAILURE"), 500
        else:
            msg = json_data["msg"]
            ScholappLogger.info(f"--- msg : {msg} ---")
            teacher_session = self._teachers_sessions[json_data["teacher"]]
            return teacher_session.add_student_msg(msg, json_data["username"], json_data["cookie"],
                                                   json_data["time"])

    def actual_get_response(self, is_teacher=False):
        json_data = flask.request.get_json()
        ScholappLogger.info(f"Json data is: {json_data}")
        if is_teacher:
            teacher_session = self._teachers_sessions[json_data["username"]]
            return teacher_session.get_student_msgs(json_data["student"], json_data["cookie"])
        else:
            teacher_session = self._teachers_sessions[json_data["teacher"]]
            return teacher_session.get_teacher_msgs(json_data["username"], json_data["cookie"])

    def actual_has_response(self):
        json_data = flask.request.get_json()
        ScholappLogger.info(f"Json data is: {json_data}")
        teacher_session = self._teachers_sessions[json_data["username"]]
        return teacher_session.teacher_has_msgs(json_data["student"], json_data["cookie"])
