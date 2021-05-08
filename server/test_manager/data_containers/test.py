import copy
import os
import pickle
import uuid
from pathlib import Path
from typing import List, Dict

from server.interfaces.jsonable import Jsonable
from server.test_manager.data_containers.interfaces.serializable import Serializable
from server.test_manager.data_containers.question import Question
from utilities.logging.scholapp_server_logger import ScholappLogger


class Test(Serializable, Jsonable):
    """
    Object to represent a test
    """

    _questions: List[Question]
    _participants: Dict[str, Dict[str, bool]]
    _test_id: str
    _classroom: str
    _teacher: str
    _name: str
    _path_to_pickled_file: Path

    def __init__(self, test_id: str = "", classroom: str = "", teacher: str = "", name: str = "",
                 start: str = "", end: str = ""):
        """
        :param test_id: the test's id
        :param classroom: the test's class
        :param teacher: the test's teacher
        :param name: the test's name
        """
        self._start = start
        self._end = end
        self._date = start.split("T")[0]
        self._questions = []
        self._test_id = test_id
        self._classroom = classroom
        self._teacher = teacher
        self._participants = {}
        self._name = name
        self._path_to_pickled_file = self._set_pickled_file_path()

    @property
    def TestId(self):
        """
        :return: the test id
        """
        return self._test_id

    @property
    def Name(self):
        """
        :return: the test name
        """
        return self._name

    @property
    def Questions(self):
        """
        :return: the test's questions
        """
        return copy.deepcopy(self._questions)

    @property
    def PickledFilePath(self):
        """
        :return: the test's pickled file path
        """
        return self._path_to_pickled_file

    @property
    def Date(self):
        return self._date

    @property
    def Start(self):
        return self._start

    @property
    def End(self):
        return self._end

    @property
    def Classroom(self):
        """
        :return: the test's class
        """
        return self._classroom

    @property
    def Teacher(self):
        """
        :return: the test's teacher
        """
        return self._teacher

    @property
    def Participants(self):
        """
        :return: the test's participants
        """
        return self._participants

    def add_participant(self, username):
        """
        Add a new participant by username

        :param username: username to add
        """
        self._participants[username] = {"is_ok": True, "should_check": False}

    def set_pickled_path(self, path):
        """
        Set the pickled path for the test

        :param path: path to pickle to
        """
        self._path_to_pickled_file = path

    def append_question(self, question: Question):
        """
        Add a question to the test

        :param question: question to add
        """
        self._questions += [question]

    def serialize(self):
        """
        Serialize the object
        """
        pickled_file = Path(self._set_pickled_file_path())
        if not pickled_file.is_file():
            pickled_file.touch()
        to_serialize = copy.deepcopy(self)
        to_serialize._path_to_pickled_file = str(self._path_to_pickled_file)
        with open(pickled_file, "wb") as pickled_file:
            pickle.dump(to_serialize, pickled_file)

    def deserialize(self):
        """
        Deserialize the object from file

        :return: self
        """
        if self._path_to_pickled_file.is_file():
            with open(self._path_to_pickled_file, "rb") as pickled_file:
                deserialized_test = pickle.load(pickled_file)
                self._questions += deserialized_test.Questions
                self._classroom = deserialized_test.Classroom
                self._path_to_pickled_file = Path(deserialized_test.PickledFilePath)
                self._date = deserialized_test.Date
                self._start = deserialized_test.Start
                self._end = deserialized_test.End
        return self

    def _set_pickled_file_path(self):
        pickled_tests = Path(os.path.join(os.path.dirname(__file__), "pickled_tests"))
        if not pickled_tests.is_dir():
            pickled_tests.mkdir()
        return pickled_tests / f"{self._test_id}.bin"

    def from_json(self, json_val: Dict):
        """
        Generate the object from a dict

        :param json_val: dict to generate from
        :return: self
        """
        if len(json_val["questions"]) == 0:
            raise Exception("The questions cannot be an empty list!!!")
        self._questions = [Question().from_json(q) for q in json_val["questions"]]
        self._classroom = json_val["classroom"]
        self._teacher = json_val["teacher"]
        self._participants = json_val["participants"]
        self._name = json_val["name"]
        self._start = json_val["start"]
        self._end = json_val["end"]
        self._date = json_val["start"].split("T")[0]
        self._test_id = str(uuid.uuid3(uuid.NAMESPACE_DNS,
                                       f"{self._teacher}+{self._classroom}+{str(self._questions)}+"
                                       f"{str(self._participants)}+{self._name}+{self._start}+"
                                       f"{self._end}+{uuid.uuid4()}"))
        ScholappLogger.info(f"Test added: {self._test_id}")
        self.serialize()
        return self

    def json(self):
        """
        :return: json representation of the object
        """
        return {
            "id": self._test_id,
            "name": self._name,
            "classroom": self._classroom,
            "teacher": self._teacher,
            "questions": [q.json() for q in self._questions],
            "start": self._start,
            "end": self._end,
            "date": self._date,
            "participants": self._participants
        }
