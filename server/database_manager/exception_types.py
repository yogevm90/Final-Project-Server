class QueryException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PermissionException(QueryException):
    def __init__(self, request, username):
        self.request = request
        self.message = 'Operation {} for {} not permitted'.format(request, username)
        super().__init__(self.message)


class WrongPasswordException(QueryException):
    def __init__(self, message, username):
        self.username = username
        self.message = 'Invalid password for {}\n {}'.format(username, message)
        super().__init__(self.message)


class InvalidRequestException(QueryException):
    def __init__(self, message):
        self.message = 'Invalid request: {}'.format(message)
        super().__init__(self.message)


class OperationFailedException(QueryException):
    def __init__(self, message):
        self.message = 'Operation failed: {}'.format(message)
        super().__init__(self.message)
