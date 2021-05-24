import flask

from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from server.database_manager.exception_types import QueryException
from server.stream_manager import stream_manager
from server.stream_manager.exceptions import StreamUserException
from utilities.logging.scholapp_server_logger import ScholappLogger
from server.database_manager.authentication_manager.authentication_manager import AuthenticationManager
from server.database_manager.data_manager.database_data_manager import DatabaseDataManager


class DBApp(FlaskAppBase):
    def __init__(self, database_name="Scholapp", import_name="DBApp", **kwargs):
        super().__init__(import_name, **kwargs)
        super()._chdir(__file__)
        self._student_methods = {
            "ById": self.student_by_id,
            "ByName": self.student_by_name
        }
        self._class_methods = {
            "ById": self.class_by_id,
            "ByName": self.class_by_name
        }
        self.valid_roles = {'teacher', 'student'}
        ScholappLogger.info(f"Setting up {import_name}")
        self._db_data_manager = DatabaseDataManager(database_name)
        self._db_auth_manager = AuthenticationManager(self._db_data_manager)
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        @self.route("/GetUser/<method>/<user_data>", methods=["POST"])
        def get_user(method, user_data):
            request_data = flask.request.get_json()
            if not self.validate_user(request_data):
                return flask.jsonify({'verdict': False, 'reason': 'wrong username or password'})
            try:
                get_user_by_data = self._student_methods[method]
                user_document = get_user_by_data(user_data)
                if 'username' not in user_document:
                    return flask.jsonify({'verdict': False, 'reason': 'User doesnt exist'})
                return flask.jsonify({'verdict': True, 'user_document': user_document})

            except QueryException as e:
                return flask.jsonify({'verdict': False, 'reason': '{}'.format(e.message)})

        @self.route("/Login", methods=["POST"])
        @self.route("/Signout", methods=["POST"])
        def login():
            request_data = flask.request.get_json()
            if self.validate_user(request_data):
                self._db_data_manager.login_user(request_data['username'])
                if self._db_data_manager.is_teacher(username=request_data['username']):
                    return flask.jsonify({'verdict': True, 'role': 'teacher'})
                else:
                    return {'verdict': True, 'role': 'student'}
            return flask.jsonify({'verdict': False, 'reason': 'wrong username or password'})

        @self.route("/Register", methods=["POST"])
        def register():
            request_data = flask.request.get_json()
            username = request_data['username']
            password = request_data['password']
            if self._db_data_manager.user_exists(username):
                return flask.jsonify({'verdict': False, 'reason': 'user already exists'})
            try:
                if request_data['role'] not in self.valid_roles:
                    return flask.jsonify({'verdict': False, 'reason': 'invalid role given'})
                self._db_data_manager.insert_user(request_data)
                stream_manager.add_user(username, password)
                user_document = self.student_by_name(username)
                return flask.jsonify({'verdict': True, 'user_document': user_document})

            except QueryException as e:
                return flask.jsonify({'verdict': False, 'reason': '{}'.format(e.message)})
            except StreamUserException as e:
                return flask.jsonify({'verdict': False, 'reason': '{}'.format(e.message)})

        @self.route("/GetClasses", methods=["POST"])
        def get_user_classes():
            request_data = flask.request.get_json()
            try:
                if not self.validate_user(request_data):
                    return flask.jsonify({'verdict': False, "classes": []})
                username = request_data['username']
                return flask.jsonify({'verdict': True, "classes": self._db_data_manager.get_classes_by_username(
                    username)})

            except QueryException:
                return flask.jsonify({'verdict': False, "classes": []})

        @self.route("/GetClass/<class_id>", methods=["POST"])
        def get_user_class_by_id(class_id):
            request_data = flask.request.get_json()
            try:
                if not self.validate_user(request_data):
                    return flask.jsonify({'verdict': False, "classes": []})
                username = request_data['username']
                classroom = None
                classes = self._db_data_manager.get_classes_by_username(username)
                for c in classes:
                    if c["class_id"] == class_id:
                        classroom = c
                        break
                if classroom is None:
                    return flask.jsonify({'verdict': False, "class": None})
                return flask.jsonify({'verdict': True, "class": classroom})

            except QueryException:
                return flask.jsonify({'verdict': False, "class": None})

        @self.route("/Details", methods=["POST"])
        def details():
            request_data = flask.request.get_json()
            try:
                if not self.validate_user(request_data):
                    return flask.jsonify({'verdict': False, 'reason': 'wrong username or password'})
                data = request_data['data']
                # case changing user
                if bool(data['username']):
                    user_doc = self.student_by_name(data['username'])
                    if bool(data['new_password']):
                        user_doc['password'] = self._db_auth_manager.get_hashed_password(request_data['new_password'])
                        stream_manager.change_password(data['username'], data['new_password'])
                    else:
                        # assign new user data from client
                        for key in data:
                            # keys from client can be empty
                            if bool(data[key]):
                                user_doc[key] = data[key]
                    self._db_data_manager.update_user(data['username'], user_doc)
                    updated_user = self._db_data_manager.get_user_by_name(data['username'])
                    return flask.jsonify({'verdict': True, 'data': updated_user})

                # case changing or inserting class
                elif 'class_' in data and data['class_'] is not None:
                    class_details = data['class']
                    class_name = class_details['class_name']
                    # update class if exists already
                    if self._db_data_manager.class_exists(class_name):
                        class_data = self.class_by_name(class_name)
                        for key in class_details:
                            # keys from client can be empty
                            if bool(class_details[key]):
                                class_data[key] = class_details[key]
                        self._db_data_manager.update_class(class_name, class_data)
                    # get updated class to send back
                    updated_class = self._db_data_manager.get_class_by_name(class_name)
                    return flask.jsonify({'verdict': True, 'data': updated_class})
                else:
                    return flask.jsonify({'verdict': False, 'reason': 'Wrong data format'})

            except QueryException as e:
                return flask.jsonify({'verdict': False, 'reason': '{}'.format(e.message)})
            except StreamUserException as e:
                return flask.jsonify({'verdict': False, 'reason': '{}'.format(e.message)})

        @self.route("/CreateClass", methods=["POST"])
        def create_class():
            request_data = flask.request.get_json()
            try:
                if not self.validate_user(request_data):
                    return flask.jsonify({'verdict': False, 'reason': 'wrong username or password'})
                class_name = request_data['class_name']
                self._db_data_manager.insert_class(request_data)
                updated_class = self._db_data_manager.get_class_by_name(class_name)
                return flask.jsonify({'verdict': True, 'data': updated_class})
            except QueryException as e:
                return flask.jsonify({'verdict': False, 'reason': '{}'.format(e.message)})

        @self.route("/GetClassroomPaths", methods=["POST"])
        def get_classroom_paths():
            request_data = flask.request.get_json()
            try:
                if not self.validate_user(request_data):
                    return flask.jsonify({'verdict': False, 'reason': 'wrong username or password'})
                class_document = self.class_by_id(request_data['class_id'])
                if 'class_id' not in class_document:
                    return {'verdict': False, 'reason': 'class doesnt exist'}
                return flask.jsonify({'verdict': True, 'data': class_document['stream_paths']})
            except QueryException as e:
                return flask.jsonify({'verdict': False, 'reason': '{}'.format(e.message)})

        @self.route("/GetPathToSave", methods=["POST"])
        def get_path_to_save():
            request_data = flask.request.get_json()
            try:
                if not self.validate_user(request_data):
                    return flask.jsonify({'verdict': False, 'reason': 'wrong username or password'})
                class_document = self.class_by_id(request_data['class_id'])
                if 'class_id' not in class_document:
                    return {'verdict': False, 'reason': 'class doesnt exist'}
                user_id = self.student_by_name(request_data['username'])['id']
                for student_path in class_document['stream_paths']:
                    if student_path['id'] == user_id:
                        return flask.jsonify({'verdict': True, 'data': student_path})
                return flask.jsonify({'verdict': False, 'reason': 'user path was not found'})

            except QueryException as e:
                return flask.jsonify({'verdict': False, 'reason': '{}'.format(e.message)})

    def student_by_id(self, student_id):
        data = self._db_data_manager.get_user_by_id(student_id)
        if data is None:
            return {}
        data.pop('password')
        data.pop('_id')
        return data

    def student_by_name(self, student_name):
        data = self._db_data_manager.get_user_by_name(student_name)
        if data is None:
            return {}
        data.pop('password')
        data.pop('_id')
        return data

    def class_by_id(self, class_id):
        data = self._db_data_manager.get_class_by_id(class_id)
        if data is None:
            return {}
        data.pop('_id')
        return data

    def class_by_name(self, class_name):
        data = self._db_data_manager.get_class_by_name(class_name)
        if data is None:
            return {}
        data.pop('_id')
        return data

    def validate_user(self, request):
        username = request['username']
        if self._db_data_manager.user_exists(username):
            if self._db_auth_manager.validate_user(username, request['password']):
                return True
        return False
