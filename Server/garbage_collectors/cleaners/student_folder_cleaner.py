import os
from pathlib import Path
from threading import Thread

from server.classroom_manager.exceptions.cleaner_is_not_running_exception import CleanerIsNotRunningException
from server.classroom_manager.process_creators.video_data_receiver import VideoDataReceiver
from server.garbage_collectors.cleaners.interfaces.cleaner_interface import CleanerInterface


class StudentFolderCleaner(CleanerInterface):
    def __init__(self, student_path_to_clean: Path, video_receiver: VideoDataReceiver):
        """
        :param student_path_to_clean: path to clean files from
        :param video_receiver: a VideoDataReceiver object
        """
        self._video_receiver = video_receiver
        self._student_path_to_clean = student_path_to_clean
        self._cleaner_thread = None
        self._running = False
        self._window_size = 99
        self._window_start = 0
        self._window_end = 0
        self._num_of_window = 0

    def start_clean(self):
        """
        Start a cleaning thread to clean the required path
        """
        self._cleaner_thread = Thread(target=self._cleaner_runner, args=(self,))
        self._cleaner_thread.start()

    def stop_clean(self):
        """
        Stop the cleaning of the folder
        """
        if self._cleaner_thread is None or not self._running:
            raise CleanerIsNotRunningException()
        self._running = False
        self._cleaner_thread.join()

    def _cleaner_runner(self):
        """
        The method that will be ran in a thread to clean the required folder
        """
        while self._running:
            self._clean_in_window()

    def _clean_in_window(self):
        """
        Will clean all files in a given window
        """
        self._window_start = self._num_of_window * self._window_size
        self._window_end = self._video_receiver.NextIncomingFileNum - 1
        if (self._video_receiver.NextIncomingFileNum + 1) % 100 == 0:
            self._num_of_window += 1
        for i in range(self._window_start, self._window_end + 1):
            file_to_check = self._student_path_to_clean / str(i)
            if file_to_check.is_file():
                os.remove(str(file_to_check))
