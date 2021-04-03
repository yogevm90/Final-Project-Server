from typing import List

from server.interfaces.jsonable import Jsonable


class Question(Jsonable):
    _question: str
    _question_num: int
    _type: str
    _options: List[str]

    def __init__(self, question: str = "", question_num: int = 0, q_type: str = "open", options: List[str] = None):
        self._question = question
        self._question_num = question_num
        self._type = q_type
        if options is None:
            options = []
        self._options = options

    def from_json(self, q_json):
        self._question = q_json["question"]
        self._question_num = q_json["question_num"]
        self._type = q_json["type"]
        self._options = q_json["options"]
        return self

    def json(self):
        return {
            "question": self._question,
            "question_num": self._question_num,
            "type": self._type,
            "options": self._options
        }
