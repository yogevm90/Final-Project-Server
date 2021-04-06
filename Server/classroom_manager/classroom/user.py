from server.classroom_manager.classroom.user_connection_details import UserConnectionDetails
from server.interfaces.jsonable import Jsonable


class User(Jsonable):
    _id: str
    _name: str
    _surname: str
    _connection_details: UserConnectionDetails

    def __init__(self, user_id, name, surname, user_connection_details: UserConnectionDetails, is_student=False,
                 is_ok=True):
        self._id = user_id
        self._name = name
        self._surname = surname
        self._is_student = is_student
        self._is_ok = is_ok
        self._connection_details = user_connection_details

    @property
    def UserId(self):
        return self._id

    @property
    def Name(self):
        return self._name

    @property
    def Surname(self):
        return self._surname

    @property
    def IP(self):
        return self._connection_details.IP

    @property
    def Port(self):
        return self._connection_details.Port

    @property
    def ConnectionDetails(self):
        return self._connection_details

    @property
    def IsStudent(self):
        return self._is_student

    def set_is_ok(self, is_ok):
        self._is_ok = is_ok

    def json(self):
        return {
            "id": self._id,
            "name": self._name,
            "surname": self._surname,
            "isStudent": self._is_student,
            "isOk": self._is_ok,
        }
