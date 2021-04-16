import json
from json import JSONDecodeError

from server.database_manager.authentication_manager.authentication_manager import AuthenticationManager
from server.database_manager.data_manager.database_data_manager import DatabaseDataManager
from server.database_manager.exception_types import InvalidRequestException, WrongPasswordException
from server.database_manager.interfaces.query_validator_interface import QueryValidatorInterface

valid_request_types = ['get', 'set']
valid_request_location = ['class', 'user']


class QueryValidator(QueryValidatorInterface):
    _db_manager: DatabaseDataManager
    _authentication_manager: AuthenticationManager

    def __init__(self, db_manager: DatabaseDataManager, authentication_manager: AuthenticationManager):
        self._db_manager = db_manager
        self._authentication_manager = authentication_manager

    def validate_query(self, request):
        # Check format
        try:
            json_obj = json.loads(request)
        except JSONDecodeError:
            raise InvalidRequestException('Request not in correct format')

        # Check user authority
        requesting_user = json_obj['username']
        requesting_password = json_obj['password']
        if not self._authentication_manager.validate_user(requesting_user, requesting_password):
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
