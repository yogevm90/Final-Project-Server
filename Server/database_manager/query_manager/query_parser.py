import json
from json import JSONDecodeError

from Server.database_manager.exception_types import InvalidRequestException, WrongPasswordException
from Server.database_manager.authentication_manager.authentication_manager import AuthenticationManager

valid_request_types = ['get', 'set']
valid_request_location = ['class', 'user']


class QueryParser:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.authentication_manager = AuthenticationManager(db_manager)

    def validate_query(self, request):
        # Check format
        try:
            json_obj = json.loads(request)
        except JSONDecodeError:
            raise InvalidRequestException('Request not in correct format')

        # Check user authority
        requesting_user = json_obj['username']
        requesting_password = json_obj['password']
        if not self.authentication_manager.validate_user(requesting_user, requesting_password):
            raise WrongPasswordException('Authentication Error', requesting_user)

        # Check request type
        request_type = json_obj['type']
        if request_type not in valid_request_types:
            raise InvalidRequestException('Request type error')

        # Check request location
        request_location = json_obj['location']
        if request_location not in valid_request_location:
            raise InvalidRequestException('Request location error')

        return json_obj
