import multiprocessing
import shutil
from multiprocessing import Manager, Process
from pathlib import Path
from typing import List

from server.classroom_manager.classroom.user import User
from server.classroom_manager.exceptions.process_creator_is_not_running_exception import \
    ProcessCreatorIsNotRunningException
from server.classroom_manager.process_creators.interfaces.process_creator_interface import ProcessCreatorInterface
from server.classroom_manager.process_creators.video_data_receiver import VideoDataReceiver
from server.classroom_manager.process_creators.video_data_sender import VideoDataSender
from server.garbage_collectors.cleaners.student_folder_cleaner import StudentFolderCleaner


class ClassroomProcessCreator(ProcessCreatorInterface):
    """
    A class to create a process that reads video data from the class' folder and cleans it when needed.
    """
    _user_processes: List[Process]
    _folder_cleaners: List[StudentFolderCleaner]

    def __init__(self, class_id: str, class_room_users_ids: list, working_dir: str):
        """
        :param class_id: the id of the class
        :param class_room_users_ids: list of student ids
        :param working_dir: the class' working dir
        """
        self._class_id = class_id
        self._working_dir = Path(working_dir) / class_id
        self._working_dir.mkdir()
        self._user_ids = class_room_users_ids
        self._manager = Manager()
        self._running = False
        self._shared_list = self._manager.list()
        self._num_of_online = multiprocessing.Value('q', 0)
        self._num_of_online.acquire()
        self._user_processes = []
        self._folder_cleaners = self._manager.list()

    def create_process(self):
        """
        Create cleaning process for the classroom's folder and reading videos from it.
        """
        self._running = True
        for user in self._user_ids:
            user_path = Path(self._working_dir) / user
            user_path.mkdir()
            user_pro = Process(target=ClassroomProcessCreator._run_student_process, args=(self._shared_list,
                                                                                          user_path,
                                                                                          self._num_of_online,
                                                                                          self._folder_cleaners))
            user_pro.start()
            self._user_processes += [user_pro]

    @property
    def IsRunning(self):
        """
        :return: True - the process is running ; False - O.W.
        """
        return self._running

    @property
    def NumOfProcesses(self):
        """
        :return: Number of processes ran
        """
        return len(self._user_processes)

    def add_user(self, user: User):
        """
        Add a new user to the cleaning process.

        :param user: the new user to add
        """
        if self._num_of_online.value > 1:
            self._num_of_online.acquire()
        self._num_of_online.value += 1
        self._shared_list.append(user)
        if self._num_of_online.value > 1:
            self._num_of_online.release()

    def remove_user(self, user_id):
        """
        Remove an existing user by id.

        :param user_id: the user's id to remove
        """
        self._num_of_online.acquire()
        self._num_of_online.value -= 1

        user = self.get_user(user_id)
        if user:
            del user
        else:
            self._num_of_online.release()
            raise AttributeError(f"The user id {user_id} is not a user id")

        if self._num_of_online.value != 1 and self._num_of_online.value != 0:
            self._num_of_online.release()

    def stop(self):
        """
        Stop the classroom cleaning process.
        """
        if not self._running:
            raise ProcessCreatorIsNotRunningException()
        while self._user_processes:
            self._folder_cleaners[0].stop_clean()
            self._user_processes[0].terminate()
            del self._user_processes[0]
            del self._folder_cleaners[0]
        shutil.rmtree(str(self._working_dir))

    @staticmethod
    def _run_student_process(shared_list: List[User], dir_path: Path, num_of_online: multiprocessing.Value,
                             cleaners: List[StudentFolderCleaner]):
        sender = VideoDataSender()
        receiver = VideoDataReceiver(dir_path)
        cleaner = StudentFolderCleaner(dir_path, receiver)
        cleaner.start_clean()
        cleaners.append(cleaner)

        while True:
            data = receiver.receive_data()
            num_of_online.acquire()
            if data:
                for user in shared_list:
                    sender.send_data(data=data, target=user.ConnectionDetails)
            num_of_online.release()

    def _try_unlock(self, val: multiprocessing.Value):
        try:
            val.release()
        except ValueError:
            self.stop()

    def get_user(self, user_id):
        for i in range(len(self._shared_list)):
            if self._shared_list[i].UserId == user_id:
                return self._shared_list[i]
        return None
