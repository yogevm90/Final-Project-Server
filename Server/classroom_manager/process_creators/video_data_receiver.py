import os
from pathlib import Path
from threading import Thread

from server.classroom_manager.process_creators.interfaces.data_receiver_interface import DataReceiverInterface
from server.classroom_manager.readers.video_reader import VideoReader


class VideoDataReceiver(DataReceiverInterface):
    """
    A class for creating objects that read new data from a folder.
    """
    def __init__(self, path: str):
        """
        :param path: path for the folder
        """
        self._path = Path(path)
        self._file_num = 0

    def receive_data(self):
        """
        Check for received data in folder.

        :return: data received
        """
        curr_file_path = self._path / str(self._file_num)

        curr_file_path_received = VideoDataReceiver._wait_for_income(curr_file_path)
        if not curr_file_path_received:
            data = None
        else:
            data = VideoReader(curr_file_path).read()
            os.remove(str(curr_file_path))

        self._file_num += 1
        return data

    @property
    def NextIncomingFileNum(self):
        """
        :return: next number of file in window
        """
        return self._file_num

    @staticmethod
    def _wait_for_income(curr_file_path: Path):
        def check_if_file_exist():
            while not curr_file_path.is_file():
                continue

        check_file_thread = Thread(target=check_if_file_exist)
        check_file_thread.start()
        check_file_thread.join(timeout=10)
        return not check_file_thread.is_alive()
