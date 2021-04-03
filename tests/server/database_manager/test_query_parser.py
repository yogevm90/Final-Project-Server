from unittest.mock import MagicMock

import pytest

from server.database_manager.exception_types import InvalidRequestException, WrongPasswordException
from server.database_manager.query_manager.query_parser import QueryValidator
from tests.server.database_manager import pre_test


@pytest.fixture(scope='session', autouse=True)
def query_parser():
    return QueryValidator(pre_test.database_manager(), MagicMock())


def test_validate_query(query_parser):
    request = '{ "username":"yoni", "password":"password", "type":"get", "location":"user" }'
    assert query_parser.validate_query(request)


def test_validate_query_wrong_query(query_parser):
    with pytest.raises(InvalidRequestException):
        request = '{ "username":"yoni", "password":"password", "type":"humus", "location":"user" }'
        query_parser.validate_query(request)


def test_validate_query_wrong_password(query_parser):
    with pytest.raises(WrongPasswordException):
        request = '{ "username":"yoni", "password":"humus", "type":"get", "location":"user" }'
        query_parser.validate_query(request)


def test_validate_query_wrong_request_format(query_parser):
    with pytest.raises(InvalidRequestException):
        request = '{ "username":"yoni", "password":"password", "zibizuvbi" }'
        query_parser.validate_query(request)
