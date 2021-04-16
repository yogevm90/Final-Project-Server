import json
import os
import traceback
import uuid
from pathlib import Path
from typing import Dict

import flask
from flask_cors import cross_origin

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from flask_microservices.test_microservice.test_user_agent_validator import TestUserAgentValidator
from server.test_manager.data_containers.test import Test
from server.test_manager.data_containers.test_container.test_container import TestContainer
from utilities.logging.scholapp_server_logger import ScholappLogger
from utilities.qrcode_creator.qrcode_creator import QRCodeCreator


class TestApp(FlaskAppBase):
    """
    Microservice for test mode
    """
    _user_redirects: Dict[str, Dict[str, object]]

    def __init__(self, import_name: str = "TestApp", **kwargs):
        """
        :param import_name: Name of the app
        """
        super().__init__(import_name, **kwargs)
        super()._chdir(__file__)
        ScholappLogger.info(f"Setting up {import_name}")
        self._user_redirects = {}
        self._setup()
        self._cookies = {}
        self._test_container = TestContainer()
        self._qr_code_generator = QRCodeCreator()
        self._port = -1
        self._submitted_tests_dir = Path(os.path.dirname(__file__)) / "submitted_tests"

        if not self._submitted_tests_dir.is_dir():
            self._submitted_tests_dir.mkdir()

        ScholappLogger.info(f"Setting up was successful")

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        self._port = port
        super().run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)

    def _setup(self):
        @self.route("/")
        def login_page():
            """
            :return: Login page
            """
            return TestApp._login_page()

        @self.route("/Login", methods=["POST"])
        def login():
            """
            Commence login

            :return: login to the server
            """
            # :TODO verify via rest
            return self.actual_login()

        @self.route("/StartTest/<test_id>/<username>")
        def start_test(test_id: str, username: str):
            """
            Start the test page creation

            :param test_id: test id
            :param username: username
            :return: the start page
            """
            return self.actual_start_test(test_id, username)

        @self.route("/CreateKey", methods=["GET"])
        def create_key():
            """
            :return: created key for the test
            """
            return self.actual_create_key()

        @self.route("/GetTest/<test_id>", methods=["POST"])
        def get_test_by_id(test_id: str):
            """
            :param test_id: test id
            :return: the test found
            """
            self._verify_login_details(flask.request.get_json())
            return flask.jsonify({"test": self._test_container.Tests[test_id].json()})

        @self.route("/GetTestByClassId/<class_id>", methods=["POST"])
        def get_test_by_class_id(class_id: str):
            """
            :param class_id class id
            :return: the tests found
            """
            self._verify_login_details(flask.request.get_json())
            tests = []
            for test in self._test_container.Tests.values():
                if test.Classroom == class_id:
                    tests += [test]

            return flask.jsonify({"tests": tests})

        @self.route("/VerifyTest", methods=["POST"])
        def verify():
            """
            :return: verification page
            """
            return self.actual_verify(flask.request.form["username"], flask.request.form["checkId"])

        @self.route("/VerifyYourTest/<test_id>/<username>")
        def verify_your_test(test_id: str, username: str):
            """
            Verify the user for the test

            :param test_id: test id
            :param username: user name
            :return: failure or success page
            """
            return self.actual_verify_your_test(test_id, username)

        @self.route("/AddTest", methods=["POST"])
        @cross_origin()
        def add_test():
            """
            Add new test

            :return: success or failure
            """
            self._verify_login_details(flask.request.get_json())
            return self.actual_add_test()

        @self.route("/AddParticipant/<test_id>", methods=["POST"])
        @cross_origin()
        def add_participant(test_id: str):
            """
            Add new participant for the test

            :return: success or failure
            """
            return self.actual_add_participant(test_id)

        @self.route("/ShouldCheckPC/<test_id>", methods=["POST"])
        def should_check_pc(test_id: str):
            """
            Check student's PC if needed

            :param test_id: as part of which test to check
            :return: True if it is needed
            """
            return self.actual_should_check_pc(test_id)

        @self.route("/MarkUserPCForCheck/<test_id>/<username>", methods=["POST"])
        def mark_user_pc_for_check(test_id: str, username: str):
            """
            Mark student's PC if needed

            :param test_id: as part of which test to check
            :param username: user to mark
            :return: True if succeeded
            """
            return self.actual_mark_user_pc_for_check(test_id, username)

        @self.route("/IsUserOk/<test_id>/<username>", methods=["POST"])
        def is_user_ok(test_id: str, username: str):
            """
            Mark student's PC if needed

            :param test_id: as part of which test to check
            :param username: user to mark
            :return: True if succeeded
            """
            return self.actual_is_user_ok(test_id, username)

        @self.route("/SubmitTest", methods=["POST"])
        def submit_test():
            """
            Submit student's test

            :return: True if succeeded
            """
            return self.actual_submit_test()

    @classmethod
    def _data_is_valid(cls, data):
        return True

    def _fail_test(self, username):
        self._user_redirects[username]["msg"] = "YOU FAILED THE TEST! \nGOOD LUCK!"

    def actual_start_test(self, test_id: str, username: str):
        """
        Create the start page

        :param test_id: test id
        :param username: username
        :return: return the rendered page
        """
        data = flask.request.get_json()
        cookie = flask.request.cookies.get("userID")
        user_data = self._cookies[cookie]

        if TestApp._data_is_valid(data) and cookie in self._cookies and \
                test_id == self._cookies[cookie]["test_id"] and user_data["username"] == username:
            redirect_url_id = self._user_redirects[username]["verification_id"]
            test_url = os.path.join("static", f"{username}.png")
            self._qr_code_generator.create({
                "url": f"http://localhost:{self._port}/VerifyYourTest/{test_id}/{username}"
            }, save_to=test_url)
            return flask.render_template("qr_code_page.html",
                                         qr_code_file=f"{username}.png",
                                         text_center=True,
                                         code=redirect_url_id)
        else:
            return flask.render_template("verification_page.html",
                                         text_center=True,
                                         failed=True,
                                         msg="")

    def actual_verify(self, username: str, verification_id: str):
        """

        :param username:
        :param verification_id:
        :return:
        """
        failed = True
        if self._verification_is_successful(username, verification_id):
            failed = False

        self._user_redirects[username]["remaining_tries"] -= 1
        return flask.render_template("verification_page.html",
                                     text_center=True,
                                     failed=failed,
                                     msg=self._user_redirects[username]["msg"])

    def _verification_is_successful(self, username: str, verification_id: str):
        result = True
        self._user_redirects[username]["msg"] = ""

        if self._user_redirects[username]["remaining_tries"] == 0:
            self._fail_test(username)
            return False

        if verification_id != self._user_redirects[username]["verification_id"]:
            result = False
            self._user_redirects[username]["msg"] += "Invalid ID inserted!\n"

        if not TestUserAgentValidator.validate(flask.request.user_agent.platform):
            result = False
            self._user_redirects[username]["remaining_tries"] = 0
            self._user_redirects[username]["msg"] = "Next time you try to insert the ID from " \
                                                    "your PC you will fail the test :)"

        return result

    def actual_verify_your_test(self, test_id: str, username: str):
        if username in self._user_redirects and test_id == self._user_redirects[username]["test_id"]:
            return flask.render_template("verify_the_student.html",
                                         test_id=test_id)
        return flask.render_template("verification_page.html",
                                     text_center=True,
                                     failed=True,
                                     msg=f"Failed to verify student for test: {test_id}")

    def actual_add_test(self):
        try:
            self._test_container.add_test(Test().from_json(flask.request.get_json()))
            return flask.jsonify({"status": "success"})
        except Exception:
            ScholappLogger.error(traceback.format_exc())
            return flask.jsonify({"status": "failure"})

    def actual_login(self):
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        test_key = flask.request.form["testKey"]
        test_id = flask.request.form["testId"]

        redirect_url_id = uuid.uuid4()
        self._user_redirects[username] = {
            "verification_id": str(redirect_url_id),
            "test_id": test_id,
            "remaining_tries": 3
        }

        ScholappLogger.info(f"User: {username} - tries to login")
        resp = flask.make_response(flask.redirect(f"/StartTest/{test_id}/{username}"))
        cookie = str(uuid.uuid3(uuid.NAMESPACE_DNS, username + password + test_key + test_id))
        self._cookies[cookie] = {"username": username, "test_id": test_id}
        resp.set_cookie("userID", cookie)
        return resp

    @staticmethod
    def _login_page():
        return flask.render_template("login_page.html",
                                     text_center=False)

    def actual_should_check_pc(self, test_id: str):
        login_details = flask.request.get_json()
        self._verify_login_details(login_details)
        username = login_details["username"]
        test = self._test_container.get_test_by_id(test_id)
        participant = test.Participants[username]
        result = participant["should_check"]
        participant["should_check"] = False
        return result

    @classmethod
    def actual_create_key(cls):
        test_key = cls._get_test_id(flask.request.get_json())
        return flask.jsonify({"test_key": test_key})

    @classmethod
    def _get_test_id(cls, data: Dict):
        data_for_id = ""
        if data:
            for key, val in data.items():
                data_for_id += f":key:{key}:val:{val}:"
        return uuid.uuid5(uuid.NAMESPACE_DNS, data_for_id)

    def actual_add_participant(self, test_id: str):
        try:
            login_details = flask.request.get_json()
            self._verify_login_details(login_details)
            username = login_details["username"]
            test = self._test_container.get_test_by_id(test_id)
            test.add_participant(username)
            return flask.jsonify({"status": "success"})
        except Exception:
            return flask.jsonify({"status": "failure"})

    def _verify_login_details(self, login_details):
        pass

    def actual_mark_user_pc_for_check(self, test_id, username):
        try:
            login_details = flask.request.get_json()
            self._verify_login_details(login_details)
            test = self._test_container.get_test_by_id(test_id)
            test[username]["should_check"] = True
            return flask.jsonify({"status": "success"})
        except Exception:
            return flask.jsonify({"status": "failure"})

    def actual_is_user_ok(self, test_id, username):
        try:
            login_details = flask.request.get_json()
            self._verify_login_details(login_details)
            test = self._test_container.get_test_by_id(test_id)
            test[username]["should_check"] = True
            return flask.jsonify({"is_ok": test[username]["is_ok"], "status": "success"})
        except Exception:
            return flask.jsonify({"status": "failure"})

    def actual_submit_test(self):
        try:
            submitted_test = flask.request.get_json()
            self._verify_login_details(submitted_test)
            test_submit_folder = self._submitted_tests_dir / submitted_test["test_id"]
            if not test_submit_folder.is_dir():
                test_submit_folder.mkdir()

            # We delete before saving
            del submitted_test["password"]
            student_submit_file = test_submit_folder / f"{submitted_test['username']}.json"
            with open(student_submit_file, "w") as student_submit_file_open:
                student_submit_file_open.write(json.dumps(submitted_test, sort_keys=True, indent=4))
            return flask.jsonify({"status": "success"})
        except Exception:
            return flask.jsonify({"status": "failure"})
