from copy import deepcopy
from threading import Lock
from datetime import datetime

import flask


class TeacherChatSession(object):
    _students_lock: Lock

    def __init__(self, teacher_name, participants, teacher_cookie):
        self.teacher_name = teacher_name
        self.teacher_cookie = teacher_cookie

        self._students = {}
        for participant in participants:
            self._students[participant] = {}

        self._students_lock = Lock()

    def add_student(self, student_name, student_cookie):
        student_exists = True
        self._students_lock.acquire()

        if student_name in self._students and self._students[student_name] == {}:
            self._students[student_name] = {
                "student_msgs": {},
                "responses": {},
                "std_lock": Lock(),
                "resp_lock": Lock(),
                "student_cookie": student_cookie
            }
        elif student_name not in self._students:
            student_exists = False

        self._students_lock.release()
        return student_exists

    def add_student_msg(self, msg, student_name, student_cookie):
        now = datetime.now()
        now = now.strftime("%m/%d/%Y, %H:%M:%S")
        self._students[student_name]["std_lock"].acquire()
        try:
            if student_name in self._students and self._students[student_name]["student_cookie"] == student_cookie:
                self._students[student_name]["student_msgs"][now] = msg
                return flask.jsonify({"status": "success"})
            else:
                return flask.make_response("FAILURE"), 500
        finally:
            self._students[student_name]["std_lock"].release()

    def get_teacher_msgs(self, student_name, student_cookie):
        self._students[student_name]["std_lock"].acquire()
        try:
            if student_name in self._students and self._students[student_name]["student_cookie"] == student_cookie:
                responses = flask.jsonify(self._students[student_name]["responses"])
                del self._students[student_name]["responses"]
                self._students[student_name]["responses"] = {}
                return responses
            else:
                return flask.make_response("FAILURE"), 500
        finally:
            self._students[student_name]["std_lock"].release()

    def add_teacher_msg(self, msg, student_name, teacher_cookie):
        if teacher_cookie != self.teacher_cookie or student_name not in self._students:
            return flask.make_response("FAILURE"), 500
        now = datetime.now()
        now = now.strftime("%m/%d/%Y, %H:%M:%S")
        self._students[student_name]["resp_lock"].acquire()
        self._students[student_name]["responses"][now] = msg
        self._students[student_name]["resp_lock"].release()
        return flask.jsonify({"status": "success"})

    def get_student_msgs(self, student_name, teacher_cookie):
        if teacher_cookie != self.teacher_cookie or student_name not in self._students:
            return flask.make_response("FAILURE"), 500

        self._students[student_name]["resp_lock"].acquire()
        result = flask.jsonify(self._students[student_name]["student_msgs"])
        del self._students[student_name]["student_msgs"]
        self._students[student_name]["student_msgs"] = {}
        self._students[student_name]["resp_lock"].release()

        return flask.jsonify({"msgs": result})

    def teacher_has_msgs(self, student_name, teacher_cookie):
        if teacher_cookie != self.teacher_cookie or student_name not in self._students:
            return flask.make_response("FAILURE"), 500

        return flask.jsonify({"has_msgs": self._students[student_name]["student_msgs"] != {}})
