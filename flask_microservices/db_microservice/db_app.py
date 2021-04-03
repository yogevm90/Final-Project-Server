import flask

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase


class DBApp(FlaskAppBase):
    def __init__(self, import_name="DBApp"):
        super().__init__(import_name)
        self._student_methods = {
            "ById": self.student_by_id,
            "ByName": self.student_by_name
        }
        self._setup()

    def _setup(self):
        @self.route("/GetStudent/<method>/<student_data>")
        def get_student(method, student_data):
            get_student_by_data = self._student_methods[method]
            return get_student_by_data(student_data)

        @self.route("/PostStudent")
        def post_student(method, student_data):
            student_to_add_json = flask.request.get_json()
            print(student_to_add_json)

    def student_by_id(self, student_id):
        print(1)
        return student_id

    def student_by_name(self, student_id):
        print(2)
        return student_id


