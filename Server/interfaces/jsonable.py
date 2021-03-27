from abc import ABC, abstractmethod


class Jsonable(ABC):
    @abstractmethod
    def json(self):
        pass
