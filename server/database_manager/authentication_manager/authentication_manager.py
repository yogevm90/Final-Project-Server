import traceback

import bcrypt

from server.database_manager.data_manager.database_data_manager import DatabaseDataManager


class AuthenticationManager(object):
    _db_data_manager: DatabaseDataManager

    def __init__(self, db_data_manager: DatabaseDataManager):
        self._db_data_manager = db_data_manager

    def validate_user(self, username, text_password):
        if not self._db_data_manager.user_exists(username):
            return False
        user_document = self._db_data_manager.get_user_by_name(username)
        hashed_password = user_document['password']
        return AuthenticationManager.check_password(text_password, hashed_password)

    @staticmethod
    def get_hashed_password(text_password):
        return bcrypt.hashpw(text_password.encode(), bcrypt.gensalt())

    @staticmethod
    def check_password(text_password, hashed_password):
        return bcrypt.checkpw(text_password.encode(), hashed_password)

    def authenticate_request(self, request_json):
        username = request_json['username']
        request_type = request_json['type']
        request_location = request_json['location']

        if request_type == 'get':
            if request_location == 'user':
                return True
            if self._db_data_manager.user_participating_class(username, request_json['username']):
                return True
        else:   # set request
            if request_location == 'user':
                if request_json['username'] == username:
                    return True
                return False
            # class request
            if self._db_data_manager.is_teacher(request_json['username']):
                return True
            return False
