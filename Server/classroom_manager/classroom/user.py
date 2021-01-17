from classroom_manager.classroom.user_connection_details import UserConnectionDetails


class User(object):
    def __init__(self, **kwargs):
        self._id = kwargs["id"]
        self._name = kwargs["name"]
        self._surname = kwargs["surname"]
        self._connection_details = UserConnectionDetails(kwargs["ip"], kwargs["port"])

    @property
    def UserId(self):
        return self._id

    @property
    def Name(self):
        return self._name

    @property
    def surname(self):
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
