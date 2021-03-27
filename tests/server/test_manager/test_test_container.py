import pytest

from server.test_manager.data_containers.test import Test
from server.test_manager.data_containers.test_container.test_container import TestContainer


def create_tests(tests, num_of_tests, tmp_path):
    for i in range(num_of_tests):
        new_test = Test(str(i))
        new_test.set_pickled_path(str(tmp_path / f"{i}.bin"))
        tests += [new_test]


@pytest.fixture
def mock_tests_sanity(tmp_path):
    tests = []
    create_tests(tests, 1000, tmp_path)
    return tests


@pytest.fixture
def mock_tests(tmp_path):
    tests = []
    create_tests(tests, 20, tmp_path)
    return tests


@pytest.fixture
def json_path(tmp_path):
    res = tmp_path / "mock.json"
    res.write_text("{}")
    return str(tmp_path / "mock.json")


def run_container_pickle_and_unpickle(tests, json_path):
    # Arrange
    test_container = TestContainer()
    test_container.set_tests_json_path(json_path)
    test_container.add_tests(tests)
    test_container.serialize()

    test_container = TestContainer()
    test_container.set_tests_json_path(json_path)
    test_container.deserialize()

    # Assert
    for expected_test, actual_test in zip(tests, test_container.Tests):
        assert expected_test.TestId == actual_test.TestId, \
            f"Unexpected test {expected_test.TestId}"
        assert expected_test.PickledFilePath == actual_test.PickledFilePath
        assert expected_test.Questions == actual_test.Questions


def test_test_container_pickle_and_unpickle(mock_tests, json_path):
    run_container_pickle_and_unpickle(mock_tests, json_path)


def test_test_container_pickle_and_unpickle_sanity(mock_tests_sanity, json_path):
    run_container_pickle_and_unpickle(mock_tests_sanity, json_path)
