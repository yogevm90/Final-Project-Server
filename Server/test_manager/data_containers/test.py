import copy
import os
import pickle
from pathlib import Path
from typing import List

from server.interfaces.jsonable import Jsonable
from server.test_manager.data_containers.interfaces.serializable import Serializable
from server.test_manager.data_containers.question import Question


class Test(Serializable, Jsonable):
    _questions: List[Question]

    def __init__(self, test_id: str):
        self._questions = []
        self._test_id = test_id
        self._path_to_pickled_file = self._get_pickled_file_path()

    @property
    def TestId(self):
        return self._test_id

    @property
    def Questions(self):
        return copy.deepcopy(self._questions)

    @property
    def PickledFilePath(self):
        return self._path_to_pickled_file

    def set_pickled_path(self, path):
        self._path_to_pickled_file = path

    def append_question(self, question: Question):
        self._questions += [question]

    def serialize(self):
        pickled_file = Path(self._path_to_pickled_file)
        if pickled_file.is_file():
            pickled_file.touch()
        with open(pickled_file, "wb") as pickled_file:
            pickle.dump(self, pickled_file)

    def deserialize(self):
        if os.path.isfile(self._path_to_pickled_file):
            with open(self._path_to_pickled_file, "rb") as pickled_file:
                deserialized_test = pickle.load(pickled_file)
                self._questions += deserialized_test.Questions
                self._path_to_pickled_file = deserialized_test.PickledFilePath

    def _get_pickled_file_path(self):
        return Path(os.path.join(os.path.dirname(__file__), "pickled_tests", f"{self._test_id}.bin"))

    def json(self):
        return {
            "id": self._test_id,
            "questions": [q.json() for q in self._questions]
        }
