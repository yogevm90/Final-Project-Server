import json
import os
import pickle
from threading import Lock
from typing import Dict, List

from server.interfaces.jsonable import Jsonable
from server.test_manager.data_containers.interfaces.serializable import Serializable
from server.test_manager.data_containers.test import Test
from utilities.logging.scholapp_server_logger import ScholappLogger


class TestContainer(Serializable, Jsonable):
    _tests_dict_path: str
    _tests_dict: Dict[str, str]
    _tests: Dict[str, Test]
    _mutex: Lock

    def __init__(self, deserialize=False):
        self._tests_json_path = os.path.join(os.path.dirname(__file__), "tests.json")
        self._mutex = Lock()
        with open(self._tests_json_path, "r") as tests_json:
            self._tests_dict = json.load(tests_json)
        self._tests = {}
        if deserialize:
            self.deserialize()

    @property
    def Tests(self) -> Dict[str, Test]:
        return self._tests

    def set_tests_json_path(self, path):
        self._serialize_json()
        self._tests_json_path = path
        with open(self._tests_json_path, "r") as tests_json:
            self._tests_dict = json.load(tests_json)

    def add_test(self, test: Test):
        self._mutex.acquire()
        ScholappLogger.info(f"Added test {test.TestId} into the container")
        self._tests[test.TestId] = test
        self._tests_dict[test.TestId] = test.PickledFilePath
        self._serialize_json()
        self._mutex.release()

    def add_tests(self, tests: List[Test]):
        for test in tests:
            self.add_test(test)

    def get_test_by_id(self, test_id: str):
        return self._tests[test_id]

    def serialize(self):
        ScholappLogger.info("Serializing tests")
        for test in self._tests.values():
            self._mutex.acquire()
            test.serialize()
            self._mutex.release()
        self._serialize_json()

    def deserialize(self):
        ScholappLogger.info("Deserializing tests")
        for test_pickle_path in self._tests_dict.values():
            self._mutex.acquire()
            with open(test_pickle_path, "rb") as test_pickle_file:
                deserialized_test = pickle.load(test_pickle_file)
                self._tests[deserialized_test.TestId] = deserialized_test
            self._mutex.release()

    def _serialize_json(self):
        ScholappLogger.info(f"Serializing tests json to: {self._tests_json_path}")
        to_save = {}
        for test_id, path in self._tests_dict.items():
            to_save[test_id] = str(path)
        with open(self._tests_json_path, "w") as tests_json:
            json.dump(to_save, tests_json)

    def json(self):
        return {
            "tests": [t.json() for t in self._tests.values()]
        }
