class ProcessCreatorIsNotRunningException(Exception):
    def __init__(self):
        super(ProcessCreatorIsNotRunningException, self).__init__("The process creator is not running, can't stop it")
