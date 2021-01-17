import multiprocessing
import shutil
from multiprocessing import Manager, Process
from pathlib import Path
from typing import List

from classroom_manager.classroom.user import User
from classroom_manager.exceptions.process_creator_is_not_running_exception import ProcessCreatorIsNotRunningException
from classroom_manager.process_creators.interfaces.process_creator_interface import ProcessCreatorInterface
from classroom_manager.process_creators.video_data_receiver import VideoDataReceiver
from classroom_manager.process_creators.video_data_sender import VideoDataSender


class ClassroomProcessCreator(ProcessCreatorInterface):
    _user_processes: List[Process]

    def __init__(self, class_id, class_room_users_ids, working_dir):
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

    def create_process(self):
        self._running = True
        for user in self._user_ids:
            user_path = Path(self._working_dir) / user
            user_path.mkdir()
            user_pro = Process(target=ClassroomProcessCreator._run_student_process, args=(self._shared_list,
                                                                                          user_path,
                                                                                          self._num_of_online))
            user_pro.start()
            self._user_processes += [user_pro]

    @property
    def IsRunning(self):
        return self._running

    @property
    def NumOfProcesses(self):
        return len(self._user_processes)

    def add_user(self, user: User):
        if self._num_of_online.value > 1:
            self._num_of_online.acquire()
        self._num_of_online.value += 1
        self._shared_list.append(user)
        if self._num_of_online.value > 1:
            self._num_of_online.release()

    def remove_user(self, user_id):
        self._num_of_online.acquire()
        self._num_of_online.value -= 1
        for i in range(len(self._shared_list)):
            if self._shared_list[i].UserId == user_id:
                del self._shared_list[i]
                break

        if self._num_of_online.value != 1 and self._num_of_online.value != 0:
            self._num_of_online.release()

    def stop(self):
        if not self._running:
            raise ProcessCreatorIsNotRunningException()
        for i in range(len(self._user_processes)):
            self._user_processes[i].terminate()
            del self._user_processes[i]
        shutil.rmtree(str(self._working_dir))

    @staticmethod
    def _run_student_process(shared_list: List[User], dir_path, num_of_online: multiprocessing.Value):
        sender = VideoDataSender()
        receiver = VideoDataReceiver(dir_path)

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
