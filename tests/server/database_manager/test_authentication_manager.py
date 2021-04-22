import pytest

from server.database_manager.authentication_manager.authentication_manager import AuthenticationManager
from tests.server.database_manager import pre_test


@pytest.fixture(scope='session', autouse=True)
def authentication_manager():
    return AuthenticationManager(pre_test.database_manager())


def test_validate_user(authentication_manager):
    assert authentication_manager.validate_user('yoni', 'password')


def test_authenticate_request_get_user(authentication_manager):
    request = {'type': 'get', 'location': 'user', 'name': 'yoni', 'username': 'haim'}
    assert authentication_manager.authenticate_request(request)
