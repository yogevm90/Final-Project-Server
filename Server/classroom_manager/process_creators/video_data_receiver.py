from pathlib import Path
from threading import Thread

from classroom_manager.process_creators.interfaces.data_receiver_interface import DataReceiverInterface
from classroom_manager.readers.video_reader import VideoReader


class VideoDataReceiver(DataReceiverInterface):
    def __init__(self, path):
        self._path = Path(path)
        self._file_num = 0

    def receive_data(self):
        curr_file_path = self._path / str(self._file_num)

        curr_file_path_received = VideoDataReceiver._wait_for_income(curr_file_path)
        if not curr_file_path_received:
            return None
        else:
            return VideoReader(curr_file_path).read()

    @staticmethod
    def _wait_for_income(curr_file_path: Path):
        def check_if_file_exist():
            while not curr_file_path.is_file():
                continue

        check_file_thread = Thread(target=check_if_file_exist)
        check_file_thread.start()
        check_file_thread.join(timeout=10)
        return not check_file_thread.is_alive()
