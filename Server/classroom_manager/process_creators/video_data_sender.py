from classroom_manager.classroom.user_connection_details import UserConnectionDetails
from classroom_manager.process_creators.interfaces.data_sender_interface import DataSenderInterface


class VideoDataSender(DataSenderInterface):
    def send_data(self, data, target: UserConnectionDetails, timeout=60):
        pass
