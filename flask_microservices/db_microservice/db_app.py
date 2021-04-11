import os

import flask

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from utilities.logging.scholapp_server_logger import ScholappLogger


class DBApp(FlaskAppBase):
    def __init__(self, import_name="DBApp", **kwargs):
        super().__init__(import_name, **kwargs)
        super()._chdir(__file__)
        self._student_methods = {
            "ById": self.student_by_id,
            "ByName": self.student_by_name
        }
        self._details_methods = {
            "username": self.student_by_id,
            "new_password": self.student_by_name,
            "name": self.student_by_name,
            "surname": self.student_by_name,
            "class": self.student_by_name
        }
        ScholappLogger.info(f"Setting up {import_name}")
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        @self.route("/GetStudent/<method>/<student_data>")
        def get_student(method, student_data):
            get_student_by_data = self._student_methods[method]
            return get_student_by_data(student_data)

        @self.route("/Register")
        def register():
            pass

        @self.route("/ChangePassword")
        def change_pass():
            pass

    def student_by_id(self, student_id):
        return student_id

    def student_by_name(self, student_id):
        return student_id


