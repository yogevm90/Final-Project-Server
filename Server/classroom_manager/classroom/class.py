from threading import Lock
from typing import List

from server.classroom_manager.classroom.user import User


class ClassContainer(object):
    def __init__(self, teacher: User, students: List[User]):
        self._lock = Lock()
        self._teacher = teacher
        self._students = students

    def __getitem__(self, key):
        self._lock.acquire()
        if key == "teacher":
            user = self._teacher
        else:
            user = self._get_student_by_id(key)
        self._lock.release()
        return user

    def _get_student_by_id(self, key):
        for student in self._students:
            if key == student.UserId:
                return student
