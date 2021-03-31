import os
import uuid
from typing import Dict

from flask import request, render_template
from werkzeug.useragents import UserAgentParser

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from flask_microservices.test_microservice.test_user_agent_validator import TestUserAgentValidator


class TestApp(FlaskAppBase):
    _user_redirects: Dict[str, Dict[str, object]]

    def __init__(self, import_name="TestApp", main_server_port=-1, server_ip=None):
        root_path = os.path.dirname(__file__)
        os.chdir(root_path)
        super().__init__(import_name, root_path=root_path)
        self._user_redirects = {}
        self._main_server_port = main_server_port
        self._server_ip = server_ip
        self._setup()
        self._user_redirects["1"] = {
            "verification_id": str(1),
            "remaining_tries": 3
        }

    def actual_start_test(self):
        data = request.get_json()
        if TestApp._data_is_valid(data):
            test_id = TestApp._get_test_id(data)
            redirect_url_id = uuid.uuid4()
            self._user_redirects[str(test_id)] = {
                "verification_id": str(redirect_url_id),
                "remaining_tries": 3
            }
            return render_template("qr_code_page.html",
                                   qr_code_file="test_url.png",
                                   text_center=True,
                                   code=redirect_url_id)
        else:
            return render_template("verification_page.html",
                                   text_center=True,
                                   failed=True,
                                   msg="")

    def _setup(self):
        @self.route("/StartTest", methods=["GET"])
        def start_test():
            return self.actual_start_test()

        @self.route("/VerifyTest/<test_id>/<verification_id>")
        def verify(test_id, verification_id):
            failed = True
            if self._verification_is_successfull(test_id, verification_id):
                failed = False
            return render_template("verification_page.html",
                                   text_center=True,
                                   failed=failed,
                                   msg=self._user_redirects[test_id]["msg"])

        @self.route("/VerifyYourTest/<test_id>")
        def verify_your_test(test_id):
            if test_id in self._user_redirects:
                return render_template("verify_the_student.html",
                                       test_id=test_id)

    @classmethod
    def _get_test_id(cls, data: Dict):
        data_for_id = ""
        if data:
            for key, val in data.items():
                data_for_id += f":key:{key}:val:{val}:"
        return uuid.uuid5(uuid.NAMESPACE_DNS, data_for_id)

    @classmethod
    def _data_is_valid(cls, data):
        return True

    def _verification_is_successfull(self, test_id, verification_id):
        result = True
        self._user_redirects[test_id]["msg"] = ""

        if self._user_redirects[test_id]["remaining_tries"] == 0:
            self._fail_test(test_id)
            return False

        if verification_id != self._user_redirects[test_id]["verification_id"]:
            result = False
            self._user_redirects[test_id]["msg"] += "Invalid ID inserted!\n"

        if not TestUserAgentValidator.validate(request.user_agent.platform):
            result = False
            self._user_redirects[test_id]["remaining_tries"] = 0
            self._user_redirects[test_id]["msg"] = "Next time you try to insert the ID from " \
                                                   "your PC you will fail the test :)"

        return result

    def _fail_test(self, test_id):
        self._user_redirects[test_id]["msg"] = "YOU FAILED THE TEST! \nGOOD LUCK!"
