import json
import os
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict

import flask
from flask_cors import cross_origin

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from flask_microservices.test_microservice.test_user_agent_validator import TestUserAgentValidator
from server.test_manager.data_containers.test import Test
from server.test_manager.data_containers.test_container.test_container import TestContainer
from utilities.decorators.in_try_catch import in_try_catch
from utilities.logging.scholapp_server_logger import ScholappLogger
from utilities.qrcode_creator.qrcode_creator import QRCodeCreator
from utilities.server_login.server_login import ServerLogin


class TestApp(FlaskAppBase):
    """
    Microservice for test mode
    """

    _user_redirects: Dict[str, Dict[str, object]]

    def __init__(self, import_name: str = "TestApp", **kwargs):
        """
        :param import_name: Name of the app
        :param kwargs: dict with any arguments needed
        """
        super().__init__(import_name, **kwargs)
        super()._chdir(__file__)
        ScholappLogger.info(f"Setting up {import_name}")
        self._user_redirects = {}
        self._setup()
        self._cookies = {}
        self._test_container = TestContainer(deserialize=True)
        self._qr_code_generator = QRCodeCreator()
        self._port = -1
        self._submitted_tests_dir = Path(os.path.dirname(__file__)) / "submitted_tests"

        if not self._submitted_tests_dir.is_dir():
            self._submitted_tests_dir.mkdir()

        ScholappLogger.info(f"Setting up was successful")

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        """
        Flask run method

        :param host: host to run on
        :param port: port to run on
        :param debug: if given, enable or disable debug mode
        :param load_dotenv: Load the nearest :file:`.env` and :file:`.flaskenv`
            files to set environment variables. Will also change the working
            directory to the directory containing the first file found
        :param options: the options to be forwarded to the underlying Werkzeug
            server.
        """
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
            try:
                TestApp._verify_login_details(flask.request.get_json())
                return flask.jsonify({"verdict": True, "test": self._test_container.Tests[test_id].json()})
            except Exception:
                return flask.jsonify({"verdict": False}), 404

        @self.route("/GetTestByClassId/<class_id>", methods=["POST"])
        def get_test_by_class_id(class_id: str):
            """
            :param class_id class id
            :return: the tests found
            """
            try:
                TestApp._verify_login_details(flask.request.get_json())
                tests = []
                for test in self._test_container.Tests.values():
                    if test.Classroom == class_id:
                        tests += [test]

                return flask.jsonify({"verdict": True, "tests": tests})
            except Exception:
                return flask.jsonify({"verdict": False}), 404

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
            :return: rendered "verify_the_student.html" in case of successful verification and "verification_page.html"
                O.W.
            """
            return self.actual_verify_your_test(test_id, username)

        @self.route("/AddTest", methods=["POST"])
        @cross_origin()
        def add_test():
            """
            Add new test

            :return: {"verdict": True} in case of success and {"verdict": False} O.W.
            """
            return self.actual_add_test()

        @self.route("/AddParticipant/<test_id>", methods=["POST"])
        @cross_origin()
        def add_participant(test_id: str):
            """
            Add new participant for the test

            :return: {"verdict": True} in case of success and {"verdict": False} O.W.

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
            :return: {"verdict": True} in case of success and {"verdict": False} O.W.

            """
            return self.actual_mark_user_pc_for_check(test_id, username)

        @self.route("/IsUserOk/<test_id>/<username>", methods=["POST"])
        def is_user_ok(test_id: str, username: str):
            """
            Mark student's PC if needed

            :param test_id: as part of which test to check
            :param username: user to mark
            :return: {"verdict": True} in case of success and {"verdict": False} O.W.

            """
            return self.actual_is_user_ok(test_id, username)

        @self.route("/SubmitTest", methods=["POST"])
        def submit_test():
            """
            Submit student's test

            :return: {"verdict": True} in case of success and {"verdict": False} O.W.

            """
            return self.actual_submit_test()

        @self.route("/SubmitUserIsInvalid/<test_id>/<username>", methods=["POST"])
        def submit_user_is_invalid(test_id, username):
            """
            Submit student is invalid

            :param test_id: test id
            :param username: username
            :return: {"verdict": True} in case of success and {"verdict": False} O.W.

            """
            return self.actual_submit_user_is_invalid(test_id, username)

        @self.route("/GetUserIsVerified/<test_id>/<username>")
        def user_is_valid(test_id, username):
            """
            Submit student is invalid

            :param test_id: test id
            :param username: username
            :return: {"verdict": True} in case of success and {"verdict": False} O.W.

            """
            if username in self._user_redirects:
                if "verified" in self._user_redirects[username]:
                    verified = self._user_redirects[username]["verified"]
                    test_id_in_redirect = self._user_redirects[username]["test_id"]
                    return flask.jsonify({"verified": verified and test_id_in_redirect == test_id, "verdict": True})
            return flask.jsonify({"verified": False, "verdict": False})

        @self.route("/SubmitUserIsValid/<test_id>/<username>", methods=["POST"])
        def submit_user_is_valid(test_id, username):
            """
            Submit student is valid

            :param test_id: test id
            :param username: username
            :return: {"verdict": True} in case of success and {"verdict": False} O.W.

            """
            return self.actual_submit_user_is_valid(test_id, username)

    def _data_is_valid(self, data):
        now = datetime.now()
        try:
            test = self._test_container.get_test_by_id(data["test_id"])
        except KeyError:
            # Test id is not valid
            return False

        start = datetime.strptime(test.Start, "%y-%m-%dT%H:%M:00")
        end = datetime.strptime(test.End, "%y-%m-%dT%H:%M:00")

        # Test didn't start yet
        if start > now or end < now:
            return False

        return True

    def _fail_test(self, username):
        self._user_redirects[username]["msg"] = "YOU FAILED THE TEST! \nGOOD LUCK!"

    @in_try_catch
    def actual_start_test(self, test_id: str, username: str):
        """
        Create the start page

        REST API: /StartTest/<test_id>/<username>

        :param test_id: test id
        :param username: username
        :return: return the rendered page
        """
        data = flask.request.get_json()
        cookie = flask.request.cookies.get("userID")
        user_data = self._cookies[cookie]

        if self._data_is_valid(data) and cookie in self._cookies and \
                test_id == user_data["test_id"] and user_data["username"] == username:
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

    @in_try_catch
    def actual_verify(self, username: str, verification_id: str):
        """
        Verify user

        REST API: /VerifyTest

        :param username:
        :param verification_id:
        :return:
        """
        failed = True
        if self._verification_is_successful(username, verification_id):
            failed = False

        self._user_redirects[username]["remaining_tries"] -= 1
        self._user_redirects[username]["verified"] = not failed
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

    @in_try_catch
    def actual_verify_your_test(self, test_id: str, username: str):
        """
        Return verification page to verify student

        REST API: /VerifyYourTest/<test_id>/<username>

        :param test_id: test id
        :param username: username
        :return: rendered "verify_the_student.html" in case of successful verification and "verification_page.html"
                O.W.
        """
        if username in self._user_redirects and test_id == self._user_redirects[username]["test_id"]:
            return flask.render_template("verify_the_student.html",
                                         test_id=test_id)
        return flask.render_template("verification_page.html",
                                     text_center=True,
                                     failed=True,
                                     msg=f"Failed to verify student for test: {test_id}")

    @in_try_catch
    def actual_add_test(self):
        """
        Add test to test container

        REST API: /AddTest

        :return: {"verdict": True} in case of success and {"verdict": False} O.W.

        """
        TestApp._verify_login_details(flask.request.get_json())
        self._test_container.add_test(Test().from_json(flask.request.get_json()))
        return flask.jsonify({"status": "success"})

    @in_try_catch
    def actual_login(self):
        """
        Login the user

        REST API: /Login

        :return: redirect to /StartTest/{test_id}/{username}
        """
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        test_key = flask.request.form["testKey"]
        test_id = flask.request.form["testId"]

        TestApp._verify_login_details({"username": username, "password": password})

        redirect_url_id = uuid.uuid4()
        self._user_redirects[username] = {
            "verification_id": str(redirect_url_id),
            "test_id": test_id,
            "remaining_tries": 3
        }

        ScholappLogger.info(f"User: {username} - tries to login")
        resp = flask.make_response(flask.redirect(f"/StartTest/{test_id}/{username}"))
        cookie = str(uuid.uuid3(uuid.NAMESPACE_DNS, username + password + test_key + test_id + redirect_url_id))
        self._cookies[cookie] = {"username": username, "test_id": test_id}
        resp.set_cookie("userID", cookie)
        return resp

    @staticmethod
    @in_try_catch
    def _login_page():
        # "/"
        return flask.render_template("login_page.html",
                                     text_center=False)

    @in_try_catch
    def actual_should_check_pc(self, test_id: str):
        """
        Check if the user should check his pc

        REST API: /ShouldCheckPC/<test_id>

        :param test_id: test id
        :return: True - if should check PC
        """
        login_details = flask.request.get_json()
        TestApp._verify_login_details(login_details)
        username = login_details["username"]
        test = self._test_container.get_test_by_id(test_id)
        participant = test.Participants[username]
        result = participant["should_check"]
        participant["should_check"] = False
        return result

    @classmethod
    @in_try_catch
    def actual_create_key(cls):
        """
        Create key for test

        REST API: /CreateKey

        :return: {"test_key": test_key}
        """
        test_key = cls._get_test_id(flask.request.get_json())
        return flask.jsonify({"test_key": test_key})

    @classmethod
    def _get_test_id(cls, data: Dict):
        data_for_id = ""
        if data:
            for key, val in data.items():
                data_for_id += f":key:{key}:val:{val}:"
        return uuid.uuid5(uuid.NAMESPACE_DNS, data_for_id)

    @in_try_catch
    def actual_add_participant(self, test_id: str):
        """
        Add test participant

        REST API: /AddParticipant/<test_id>

        :param test_id: test id to add participant to
        :return: {"verdict": True} in case of success and {"verdict": False} O.W.

        """
        login_details = flask.request.get_json()
        TestApp._verify_login_details(login_details)
        username = login_details["username"]
        test = self._test_container.get_test_by_id(test_id)
        test.add_participant(username)
        return flask.jsonify({"verdict": True})

    @staticmethod
    def _verify_login_details(login_details):
        assert ServerLogin.login(login_details["username"], login_details["password"]), \
            "Unable to login into the server"

    @in_try_catch
    def actual_mark_user_pc_for_check(self, test_id, username):
        """
        Mark a user to check his PC

        REST API: /MarkUserPCForCheck/<test_id>/<username>

        :param test_id: test id
        :param username: username
        :return: {"verdict": True} in case of success and {"verdict": False} O.W.

        """
        login_details = flask.request.get_json()
        TestApp._verify_login_details(login_details)
        test = self._test_container.get_test_by_id(test_id)
        test[username]["should_check"] = True
        return flask.jsonify({"verdict": True})

    @in_try_catch
    def actual_is_user_ok(self, test_id, username):
        """
        Validate whether the user is ok

        REST API: /IsUserOk/<test_id>/<username>

        :param test_id: test id
        :param username: user name
        :return: {"verdict": True} in case of success and {"verdict": False} O.W.

        """
        login_details = flask.request.get_json()
        TestApp._verify_login_details(login_details)
        test = self._test_container.get_test_by_id(test_id)
        test[username]["should_check"] = True
        return flask.jsonify({"is_ok": test[username]["is_ok"], "verdict": True})

    @in_try_catch
    def actual_submit_user_is_invalid(self, test_id, username):
        """
        Submit that the user is not valid

        :param username: username
        :param test_id: test id
        :return: {"verdict": True} in case of success and {"verdict": False} O.W.

        """
        return self._change_is_ok(test_id, username, False)

    @in_try_catch
    def actual_submit_user_is_valid(self, test_id, username):
        """
        Submit that the user is valid

        :param username: username
        :param test_id: test id
        :return: {"verdict": True} in case of success and {"verdict": False} O.W.
        """
        return self._change_is_ok(test_id, username)

    def _change_is_ok(self, test_id, username, val: bool = True):
        login_details = flask.request.get_json()
        TestApp._verify_login_details(login_details)
        test = self._test_container.get_test_by_id(test_id)
        test[username]["is_ok"] = val
        return flask.jsonify({"verdict": True})

    @in_try_catch
    def actual_submit_test(self):
        """
        Submit the test

        REST API: /SubmitTest

        :return: {"verdict": True} in case of success and {"verdict": False} O.W.
        """
        submitted_test = flask.request.get_json()
        TestApp._verify_login_details(submitted_test)
        test_submit_folder = self._submitted_tests_dir / submitted_test["test_id"]
        if not test_submit_folder.is_dir():
            test_submit_folder.mkdir()

        # We delete before saving
        if "password" in submitted_test:
            del submitted_test["password"]
        student_submit_file = test_submit_folder / f"{submitted_test['username']}.json"
        with open(student_submit_file, "w") as student_submit_file_open:
            student_submit_file_open.write(json.dumps(submitted_test, sort_keys=True, indent=4))
        return flask.jsonify({"verdict": True})
