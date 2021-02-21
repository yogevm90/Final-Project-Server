from abc import ABC, abstractmethod

from server.classroom_manager.classroom.user_connection_details import UserConnectionDetails


class DataSenderInterface(ABC):
    @abstractmethod
    def send_data(self, data, target: UserConnectionDetails, timeout=60):
        pass
