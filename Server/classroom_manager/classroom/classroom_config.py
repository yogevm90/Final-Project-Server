from datetime import datetime
import datetime as dt
from threading import Lock
from typing import List

from server.classroom_manager.classroom.user import User
from server.interfaces.jsonable import Jsonable


class ClassroomConfig(Jsonable):
    _classroom_id: str
    _user_ids: List[str]
    _start: str
    _end: str
    _day: int
    _teacher: User
    _students: List[User]

    SPECIAL_LIST_SEP = ","

    def __init__(self, classroom_id: str, user_ids: List[str], start: str, end: str,
                 day: int, teacher: User, students: List[User], homework_links: str,
                 external_links: str, class_updates: str):
        self._classroom_id = classroom_id
        self._user_ids = user_ids
        self._start = start
        self._end = end
        self._day = day
        self._teacher = teacher
        self._students = students
        self._homework_links = homework_links.split(ClassroomConfig.SPECIAL_LIST_SEP)
        self._external_links = external_links.split(ClassroomConfig.SPECIAL_LIST_SEP)
        self._class_updates = class_updates.split(ClassroomConfig.SPECIAL_LIST_SEP)
        self._mutex = Lock()

    @property
    def ID(self):
        return self._classroom_id

    @property
    def UserIds(self):
        return self._user_ids

    @property
    def Start(self):
        return self._start

    @property
    def End(self):
        return self._end

    @property
    def DateInCurrWeek(self) -> datetime:
        today = datetime.now()
        dates_in_week = [today + dt.timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]
        return dates_in_week[self._day - 1]

    def add_student(self, student: User):
        if not student.IsStudent:
            raise RuntimeError(f"{student.Name} {student.Surname} is not a student")
        self._mutex.acquire()
        self._students += [student]
        self._mutex.release()

    def remove_student(self, student: User):
        self._mutex.acquire()
        del student
        self._mutex.release()

    def json(self):
        curr_date = self.DateInCurrWeek
        return {
            "start": f"{curr_date.year}:{curr_date.month}:{curr_date.day}T{self._start}",
            "end": f"{curr_date.year}:{curr_date.month}:{curr_date.day}T{self._end}",
            "students": [student.json() for student in self._students],
            "teacher": self._teacher.json()
        }
