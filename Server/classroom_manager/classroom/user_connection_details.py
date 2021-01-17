class UserConnectionDetails(object):
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port

    @property
    def IP(self):
        return self._ip

    @property
    def Port(self):
        return self._port
