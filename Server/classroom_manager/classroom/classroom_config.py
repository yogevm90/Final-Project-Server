class ClassroomConfig(object):
    def __init__(self, classroom_id, user_ids, working_dir):
        self._classroom_id = classroom_id
        self._user_ids = user_ids
        self._working_dir = working_dir

    @property
    def ID(self):
        return self._classroom_id

    @property
    def UserIds(self):
        return self._user_ids

    @property
    def WorkingDir(self):
        return self._working_dir
