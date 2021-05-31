from collections import OrderedDict, defaultdict
from threading import Lock

import flask

from utilities.logging.scholapp_server_logger import ScholappLogger


class TeacherChatSession(object):
    _students_lock: Lock

    def __init__(self, teacher_name, participants, teacher_cookie):
        self.teacher_name = teacher_name
        self.teacher_cookie = teacher_cookie
        self._num_of_msgs = 0
        self._num_of_msgs_lock = Lock()

        self._students = {}
        self._students_prev_num_of_msgs = defaultdict(lambda: 0)
        for participant in participants:
            ScholappLogger.info(f"Adding participant: {participant}")
            self._students[participant["name"]] = {
                "student_msgs": OrderedDict(),
                "responses": OrderedDict(),
                "std_lock": Lock(),
                "resp_lock": Lock(),
            }

        self._students_lock = Lock()

    def add_student(self, student_name, student_cookie):
        student_exists = True
        self._students_lock.acquire()

        if student_name in self._students and self._students[student_name] == {}:
            self._students[student_name]["cookie"] = student_cookie
        elif student_name not in self._students:
            student_exists = False

        self._students_lock.release()
        return student_exists

    def add_student_msg(self, msg, student_name, student_cookie, key_time):
        self._students[student_name]["std_lock"].acquire()
        try:
            if student_name in self._students and self._students[student_name]["cookie"] == student_cookie:
                self._students[student_name]["student_msgs"][self._num_of_msgs] = {"msg": msg, "time": key_time}
                self._num_of_msgs_lock.acquire()
                self._num_of_msgs += 1
                self._num_of_msgs_lock.release()
                return flask.jsonify({"status": "success"})
            else:
                return flask.make_response("FAILURE"), 500
        finally:
            self._students[student_name]["std_lock"].release()

    def get_teacher_msgs(self, student_name, student_cookie):
        self._students[student_name]["std_lock"].acquire()
        try:
            if student_name in self._students and self._students[student_name]["cookie"] == student_cookie:
                msgs = self._students[student_name]["responses"]
                ur_msgs = self._students[student_name]["student_msgs"]

                to_send = TeacherChatSession._create_to_send(msgs, ur_msgs)

                result = flask.jsonify({"msgs": to_send, "n": len(to_send)})
                return result
            else:
                return flask.make_response("FAILURE"), 500
        finally:
            self._students[student_name]["std_lock"].release()

    def add_teacher_msg(self, msg, student_name, teacher_cookie, key_time):
        if teacher_cookie != self.teacher_cookie or student_name not in self._students:
            return flask.make_response("FAILURE"), 500
        self._students[student_name]["resp_lock"].acquire()
        self._students[student_name]["responses"][self._num_of_msgs] = {"msg": msg, "time": key_time}
        self._num_of_msgs_lock.acquire()
        self._num_of_msgs += 1
        self._num_of_msgs_lock.release()
        self._students[student_name]["resp_lock"].release()
        return flask.jsonify({"status": "success"})

    def get_student_msgs(self, student_name, teacher_cookie):
        if teacher_cookie != self.teacher_cookie or student_name not in self._students:
            return flask.make_response("FAILURE"), 500

        self._students[student_name]["resp_lock"].acquire()
        msgs = self._students[student_name]["student_msgs"]
        ur_msgs = self._students[student_name]["responses"]
        to_send = TeacherChatSession._create_to_send(msgs, ur_msgs)

        result = flask.jsonify({"msgs": to_send, "n": len(to_send)})
        self._students[student_name]["resp_lock"].release()

        return result

    @staticmethod
    def _create_to_send(msgs, ur_msgs):
        to_send = OrderedDict()
        for key, msg in msgs.items():
            to_send[key] = {"msg": msg["msg"], "time": msg["time"], "type": "r"}

        for key, msg in ur_msgs.items():
            to_send[key] = {"msg": msg["msg"], "time": msg["time"], "type": "s"}

        return to_send

    def teacher_has_msgs(self, student_name, teacher_cookie):
        if teacher_cookie != self.teacher_cookie or student_name not in self._students:
            return flask.make_response("FAILURE"), 500

        # What we do here is if the teacher already got notified with the new messages
        # he won't get notified again that he has ones
        std_msgs_len = len(self._students[student_name]["student_msgs"])
        prev_std_msgs_len = self._students_prev_num_of_msgs[student_name]
        self._students_prev_num_of_msgs[student_name] = std_msgs_len
        return flask.jsonify({"has_msgs": std_msgs_len != prev_std_msgs_len})
