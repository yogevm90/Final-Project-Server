import bcrypt


class AuthenticationManager:
    def __init__(self, db_data_manager):
        self.db_data_manager = db_data_manager

    def validate_user(self, username, text_password):
        user_document = self.db_data_manager.get_user_by_name(username)
        hashed_password = user_document['password']
        return self.check_password(text_password, hashed_password)

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

        if self.check_if_admin(username):
            return True

        if request_type == 'get':
            if request_location == 'user':
                return True
            if self.db_data_manager.user_participating_class(username, request_json['name']):
                return True
        else:   # set request
            if request_location == 'user':
                if request_json['name'] == username:
                    return True
                return False
            # class request
            if self.db_data_manager.is_teacher(username, request_json['name']):
                return True
            return False

    def check_if_admin(self, username):
        user_document = self.db_data_manager.get_user_by_name(username)
        try:
            if user_document['admin']:
                return True
        except:
            return False
