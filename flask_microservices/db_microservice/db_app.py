from flask_microservices.flask_executor.flask_app_base import FlaskAppBase
from server.database_manager.exception_types import QueryException
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
        self._details_methods = {
            "username": self.student_by_id,
            "new_password": self.student_by_name,
            "name": self.student_by_name,
            "surname": self.student_by_name,
            "class": self.student_by_name
        }
        ScholappLogger.info(f"Setting up {import_name}")
        self._db_data_manager = DatabaseDataManager(database_name)
        self._db_auth_manager = AuthenticationManager(self._db_data_manager)
        self._setup()
        ScholappLogger.info(f"Setting up was successful")

    def _setup(self):
        @self.route("/GetUser/<method>/<user_data>")
        def get_user(method, user_data, request_data):
            if not self.validate_user(request_data):
                return {'verdict': False, 'reason': 'wrong username or password'}
            try:
                get_user_by_data = self._student_methods[method]
                user_document = get_user_by_data(user_data)
                return {'verdict': True, 'user_document': user_document}

            except QueryException as e:
                return {'verdict': False, 'reason': '{}'.format(e.message)}

        @self.route("/SetUser/<method>/<user_data>")
        def set_user(method, user_data, request_data):
            try:
                if not self.validate_user(request_data):
                    return {'verdict': False, 'reason': 'wrong username or password'}
                get_user_by_data = self._student_methods[method]
                user_document = get_user_by_data(user_data)
                if user_document['username'] != user_data and user_document['id'] != user_data:
                    return {'verdict': False, 'reason': 'Operation not allowed'}
                details = request_data['details']
                for key in details:
                    user_document[key] = details[key]
                self._db_data_manager.update_user(user_document['username'], user_document)
                updated_user = self._db_data_manager.get_user_by_name(user_document['username'])
                return {'verdict': True, 'user_document': updated_user}

            except QueryException as e:
                return {'verdict': False, 'reason': '{}'.format(e.message)}

        @self.route("/SetClass/<method>/<class_data>")
        def set_class(method, class_data, request_data):
            try:
                if not self.validate_user(request_data):
                    return {'verdict': False, 'reason': 'wrong username or password'}
                get_class_by_data = self._class_methods[method]
                class_document = get_class_by_data(class_data)
                details = request_data['details']
                if details['teacher_name'] != class_document['teacher_name']:
                    return {'verdict': False, 'reason': 'Operation not allowed'}
                for key in details:
                    class_document[key] = details[key]
                self._db_data_manager.update_class(class_document['name'], class_document)
                updated_class = self._db_data_manager.get_class_by_name(class_document['name'])
                return {'verdict': True, 'class_document': updated_class}

            except QueryException as e:
                return {'verdict': False, 'reason': '{}'.format(e.message)}

        @self.route("/Login")
        @self.route("/Signout")
        def login(request_data):
            if self.validate_user(request_data):
                if self._db_data_manager.is_teacher(username=request_data['username']):
                    return {'verdict': True, 'role': 'teacher'}
                else:
                    return {'verdict': True, 'role': 'student'}
            return {'verdict': False, 'reason': 'wrong username or password'}

        @self.route("/Register")
        def register(request_data):
            if self._db_data_manager.user_exists(request_data['username']):
                return {'verdict': False, 'reason': 'user already exists'}
            try:
                self._db_data_manager.insert_user(request_data)
                user_document = self.student_by_name(request_data['username'])
                return {'verdict': True, 'user_document': user_document}

            except QueryException as e:
                return {'verdict': False, 'reason': '{}'.format(e.message)}

        @self.route("/ChangePassword")
        def change_password(request_data):
            try:
                if self.validate_user(request_data):
                    username = request_data['username']
                    user_doc = self._db_data_manager.get_user_by_name(username)
                    user_doc['password'] = self._db_auth_manager.get_hashed_password(request_data['new_password'])
                    self._db_data_manager.update_user(username, user_doc)
                    return {'verdict': True}
                else:
                    return {'verdict': False, 'reason': 'wrong password'}

            except QueryException as e:
                return {'verdict': False, 'reason': '{}'.format(e.message)}

        @self.route("/GetClasses")
        def get_user_classes(request_data):
            try:
                if not self.validate_user(request_data):
                    return []
                username = request_data['username']
                return self._db_data_manager.get_classes_by_username(username)

            except QueryException:
                return []

        @self.route("/CreateClass")
        def create_class(request_data):
            try:
                if not self.validate_user(request_data):
                    return {'verdict': False, 'reason': 'wrong username or password'}
                if not self._db_data_manager.is_teacher(request_data['teacher_name']):
                    return {'verdict': False, 'reason': '{} is not a teacher'.format(request_data['teacher_name'])}
                request_data.pop('username')
                request_data.pop('password')
                self._db_data_manager.insert_class(request_data)
                class_document = self._db_data_manager.get_user_by_name(request_data['name'])
                return {'verdict': True, 'class_document': self.class_by_name(class_document)}

            except QueryException as e:
                return {'verdict': False, 'reason': '{}'.format(e.message)}

        @self.route("/Details")
        def details(request_data):
            try:
                if not self.validate_user(request_data):
                    return {'verdict': False, 'reason': 'wrong username or password'}
                data = request_data['data']
                current_data = {}
                if 'user' in data:
                    user_data = data['user']
                    if 'username' in user_data:
                        current_data = self.student_by_name(user_data['username'])
                    elif 'id' in user_data:
                        current_data = self.student_by_id(user_data['id'])
                    for key in user_data:
                        current_data[key] = user_data[key]
                    self._db_data_manager.update_user(current_data['username'], current_data)
                elif 'class' in data:
                    class_data = data['class']
                    if 'name' in class_data:
                        current_data = self.class_by_name(class_data['name'])
                    elif 'id' in class_data:
                        current_data = self.class_by_id(class_data['id'])
                    for key in class_data:
                        current_data[key] = class_data[key]
                    self._db_data_manager.update_class(current_data['name'], current_data)
                else:
                    return {'verdict': False, 'reason': 'Wrong data format'}
                return {'verdict': True, 'data': current_data}

            except QueryException as e:
                return {'verdict': False, 'reason': '{}'.format(e.message)}

        @self.route("/GetClassroomPaths")
        def get_classroom_paths(request_data):
            try:
                if not self.validate_user(request_data):
                    return {'verdict': False, 'reason': 'wrong username or password'}
                class_document = self.class_by_id(request_data['class_id'])
                return {'verdict': True, 'data': class_document['stream_paths']}
            except QueryException as e:
                return {'verdict': False, 'reason': '{}'.format(e.message)}

        @self.route("/GetPathToSave")
        def get_path_to_save(request_data):
            try:
                if not self.validate_user(request_data):
                    return {'verdict': False, 'reason': 'wrong username or password'}
                class_document = self.class_by_id(request_data['class_id'])
                user_id = self.student_by_name(request_data['username'])['id']
                for student_path in class_document['stream_paths']:
                    if student_path['user_id'] == user_id:
                        return {'verdict': True, 'data': student_path}
                return {'verdict': False, 'reason': 'user path was not found'}

            except QueryException as e:
                return {'verdict': False, 'reason': '{}'.format(e.message)}

    def student_by_id(self, student_id):
        data = self._db_data_manager.get_user_by_id(student_id)
        if data is None:
            return {}
        data.pop('password')
        return data

    def student_by_name(self, student_name):
        data = self._db_data_manager.get_user_by_name(student_name)
        if data is None:
            return {}
        data.pop('password')
        return data

    def class_by_id(self, class_id):
        data = self._db_data_manager.get_class_by_id(class_id)
        if data is None:
            return {}
        return data

    def class_by_name(self, class_name):
        data = self._db_data_manager.get_class_by_name(class_name)
        if data is None:
            return {}
        return data

    def validate_user(self, request):
        if self._db_data_manager.user_exists(request['username']):
            if self._db_auth_manager.validate_user(request['username'], request['password']):
                return True
        return False
