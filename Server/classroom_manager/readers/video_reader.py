from classroom_manager.readers.interfaces.reader import Reader


class VideoReader(Reader):
    def __init__(self, path):
        self._path = path

    def read(self):
        pass
