class CleanerIsNotRunningException(Exception):
    def __init__(self):
        super(CleanerIsNotRunningException, self).__init__("The cleaner is not running, can't stop it")
