from typing import List

from server.interfaces.jsonable import Jsonable


class Question(Jsonable):
    def __init__(self, question: str, question_num: int):
        self._question_num = question_num
        self._question = question

    def json(self):
        return {
            "question": self._question,
            "question_num": self._question_num,
            "type": "open",
            "options": []
        }


class MultiQuestion(Question):
    _options: List[str]

    def __init__(self, question: str, question_num: int, options: List[str] = None):
        super().__init__(question, question_num)
        if options is None:
            options = []
        self._options = options

    def add_option(self, option: str):
        self._options += [option]

    def json(self):
        res = super(MultiQuestion, self).json()
        res["options"] += self._options
        res["type"] = "multi"
        return res
