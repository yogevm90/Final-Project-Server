from abc import ABC, abstractmethod


class QueryExecutorInterface(ABC):
    @abstractmethod
    def execute_query(self, *args, **kwargs):
        pass
