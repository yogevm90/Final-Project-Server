import os
import uuid
from collections import defaultdict
from pathlib import Path
from threading import Lock
from typing import Dict, List

import flask
from flask_cors import CORS
from pyomo.solvers.tests.checks.test_CPLEXDirect import TestAddCon

from flask_microservices.chat_microservice.teacher_chat_session import TeacherChatSession
from server.interfaces.jsonable import Jsonable
from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from utilities.logging.scholapp_server_logger import ScholappLogger

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

        @self.route("/TeacherGetMessages")
        def teacher_get_messages():
            return self.actual_get_response(is_teacher=True)

        @self.route("/TeacherHasNewMessages")
        def student_get_messages():
            return self.actual_has_response()

        @self.route("/StudentGetMessages")
        def student_get_messages():
            return self.actual_get_response()

    def _verify_login_details(self, username, password, is_teacher=False):
        pass

    def actual_open_session(self, is_teacher=False):
        json_data = flask.request.get_json()
        self._verify_login_details(username=json_data["username"], password=json_data["password"],
                                   is_teacher=is_teacher)

        cookie = str(uuid.uuid3(uuid.NAMESPACE_DNS, json_data["username"] + json_data["password"] + str(uuid.uuid4())))

        if is_teacher:
            self._teachers_sessions[json_data["username"]] = TeacherChatSession(json_data["username"],
                                                                                json_data["participants"],
                                                                                cookie)
        else:
            if json_data["teacher"] in self._teachers_sessions:
                student_exists = self._teachers_sessions[json_data["teacher"]].add_student(json_data["username"],
                                                                                           cookie)
                if not student_exists:
                    return flask.make_response("Failure"), 500

        resp = flask.make_response(flask.jsonify({"status": "success"}))

        if is_teacher:
            resp.set_cookie(TEACHER_COOKIE_KEY, cookie)
        else:
            resp.set_cookie(STUDENT_COOKIE_KEY, cookie)

        return resp

    def actual_send_response(self, is_teacher=False):
        json_data = flask.request.get_json()
        if is_teacher:
            cookie = flask.request.cookies.get(TEACHER_COOKIE_KEY)
            if json_data["username"] in self._teachers_sessions:
                teacher_session = self._teachers_sessions[json_data["username"]]
                return teacher_session.add_teacher_msg(json_data["msg"], json_data["student"], cookie)
            else:
                return flask.make_response("FAILURE"), 500
        else:
            cookie = flask.request.cookies.get(STUDENT_COOKIE_KEY)
            teacher_session = self._teachers_sessions[json_data["teacher"]]
            return teacher_session.add_student_msg(json_data["msg"], json_data["username"], cookie)

    def actual_get_response(self, is_teacher=False):
        json_data = flask.request.get_json()
        if is_teacher:
            cookie = flask.request.cookies.get(TEACHER_COOKIE_KEY)
            teacher_session = self._teachers_sessions[json_data["username"]]
            return teacher_session.get_student_msgs(json_data["student"], cookie)
        else:
            cookie = flask.request.cookies.get(STUDENT_COOKIE_KEY)
            teacher_session = self._teachers_sessions[json_data["teacher"]]
            return teacher_session.get_teacher_msgs(json_data["username"], cookie)

    def actual_has_response(self):
        json_data = flask.request.get_json()
        cookie = flask.request.cookies.get(TEACHER_COOKIE_KEY)
        teacher_session = self._teachers_sessions[json_data["username"]]
        return teacher_session.teacher_has_msgs(json_data["student"], cookie)
