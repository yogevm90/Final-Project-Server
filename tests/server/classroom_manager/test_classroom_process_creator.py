from time import sleep
from unittest import mock
from unittest.mock import MagicMock

import pytest

from server.classroom_manager.classroom.user import User
from server.classroom_manager.exceptions.process_creator_is_not_running_exception import \
    ProcessCreatorIsNotRunningException
from server.classroom_manager.process_creators.classroom_process_creator import ClassroomProcessCreator
from server.classroom_manager.process_creators.video_data_receiver import VideoDataReceiver
from server.classroom_manager.process_creators.video_data_sender import VideoDataSender


@pytest.fixture
def classroom_process_creator(tmp_path):
    class_id = "1234"
    user_ids = ["1", "2", "3"]

    return ClassroomProcessCreator(class_id, user_ids, tmp_path)


@pytest.fixture
def user1():
    kwargs = {
        "id": "1",
        "name": "mock1",
        "surname": "surmock1",
        "ip": "1.1.1.1",
        "port": "1111"
    }
    return User(**kwargs)


@pytest.fixture
def video_data_receiver_mock(monkeypatch):
    mocked_obj = MagicMock()

    def my_init(self, *args, **kwargs):
        return mocked_obj

    monkeypatch.setattr(VideoDataReceiver, "__init__", my_init)
    return mocked_obj


@pytest.fixture
def video_data_sender_mock(monkeypatch):
    mocked_obj = MagicMock()

    def my_init(self, path, *args, **kwargs):
        return mocked_obj

    monkeypatch.setattr(VideoDataSender, "__init__", my_init)
    return mocked_obj


def test_full_flow(video_data_sender_mock, video_data_receiver_mock, tmp_path, classroom_process_creator, user1, user2):
    classroom_process_creator.create_process()

    classroom_process_creator.add_user(user1)

    classroom_process_creator.remove_user(user1.UserId)

    classroom_process_creator.stop()

    assert len([class_dir for class_dir in tmp_path.iterdir()]) == 0
    assert not classroom_process_creator.IsRunning
    assert classroom_process_creator.NumOfProcesses == 0


def test_stop_exception(classroom_process_creator):
    with pytest.raises(ProcessCreatorIsNotRunningException):
        classroom_process_creator.stop()
