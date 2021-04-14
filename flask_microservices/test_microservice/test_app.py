import os
import traceback
import uuid
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

    def __init__(self, import_name="TestApp", **kwargs):
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
        ScholappLogger.info(f"Setting up was successful")

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        self._port = port
        super().run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)

    def _setup(self):
        @self.route("/", methods=["GET"])
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

        @self.route("/StartTest/<test_id>/<username>", methods=["GET"])
        def start_test(test_id, username):
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

        @self.route("/GetTest/<test_id>", methods=["GET"])
        def get_test_by_id(test_id):
            """
            :param test_id: test id
            :return: the test found
            """
            # :TODO verify via rest
            return flask.jsonify({"test": self._test_container.Tests[test_id]})

        @self.route("/GetTestByClassId/<class_id>", methods=["GET"])
        def get_test_by_class_id(class_id):
            """
            :param class_id class id
            :return: the tests found
            """
            # :TODO verify via rest
            found_test = None
            for test in self._test_container.Tests.values():
                if test.Classroom == class_id:
                    found_test = test

            if found_test:
                return flask.jsonify(found_test.json())
            else:
                return flask.make_response("failed"), 404

        @self.route("/VerifyTest", methods=["POST"])
        def verify():
            """
            :return: verification page
            """
            return self.actual_verify(flask.request.form["username"], flask.request.form["checkId"])

        @self.route("/VerifyYourTest/<test_id>/<username>")
        def verify_your_test(test_id, username):
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
            return self.actual_add_test()

        @self.route("/ShouldCheckPC/<test_id>/<username>", methods=["POST"])
        def should_check_pc(test_id, username):
            """
            Check student's PC if needed
            :param test_id: as part of which test to check
            :param username: username
            :return: True if it is needed
            """
            return self.actual_should_check_pc(test_id, username)

    @classmethod
    def _data_is_valid(cls, data):
        return True

    def _fail_test(self, username):
        self._user_redirects[username]["msg"] = "YOU FAILED THE TEST! \nGOOD LUCK!"

    def actual_start_test(self, test_id, username):
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

    def actual_verify(self, username, verification_id):
        failed = True
        if self._verification_is_successful(username, verification_id):
            failed = False

        self._user_redirects[username]["remaining_tries"] -= 1
        return flask.render_template("verification_page.html",
                                     text_center=True,
                                     failed=failed,
                                     msg=self._user_redirects[username]["msg"])

    def _verification_is_successful(self, username, verification_id):
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

    def actual_verify_your_test(self, test_id, username):
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

    def actual_should_check_pc(self, test_id, username):
        login_details = flask.request.get_json()

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
