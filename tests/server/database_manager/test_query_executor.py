import pytest

from Server.database_manager.query_manager.query_executor import QueryExecutor
from tests.server.database_manager import pre_test


@pytest.fixture(scope='session', autouse=True)
def query_executor():
    return QueryExecutor(pre_test.database_manager())


def test_execute_query_get_user(query_executor):
    user_details = query_executor._get_request('user', 'yoni')
    assert user_details['age'] == 3


def test_execute_query_get_class(query_executor):
    class_details = query_executor._get_request('class', 'class1')
    assert class_details['teacher'] == 'dana'


def test_execute_query_set_user(query_executor):
    query = {'type': 'set', 'location': 'user', 'name': 'lily', 'data': {'details': {'age': 5}}}
    updated_user_details = query_executor.execute_query(query)
    assert updated_user_details['age'] == 5


def test_execute_query_set_class(query_executor):
    query = {'type': 'set', 'location': 'class', 'name': 'class1', 'data': {'teacher': 'moshe'}}
    updated_class_details = query_executor.execute_query(query)
    assert updated_class_details['teacher'] == 'moshe'
