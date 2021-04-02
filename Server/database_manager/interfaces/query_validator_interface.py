from abc import ABC, abstractmethod


class QueryValidatorInterface(ABC):
    @abstractmethod
    def validate_query(self, *args, **kwargs):
        pass
