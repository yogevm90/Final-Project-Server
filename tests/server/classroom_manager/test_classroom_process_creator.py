from unittest import mock

import pytest

from server.classroom_manager.classroom.user import User
from server.classroom_manager.process_creators.classroom_process_creator import ClassroomProcessCreator


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
def user2():
    kwargs = {
        "id": "2",
        "name": "mock",
        "surname": "surmock",
        "ip": "2.2.2.2",
        "port": "2222"
    }
    return User(**kwargs)


@mock.patch("classroom_manager.process_creators.video_data_receiver.VideoDataReceiver")
@mock.patch("classroom_manager.process_creators.video_data_sender.VideoDataSender")
def test_full_flow(video_data_sender_mock, video_data_receiver_mock, tmp_path, classroom_process_creator, user1, user2):
    classroom_process_creator.create_process()

    classroom_process_creator.add_user(user1)
    classroom_process_creator.add_user(user2)

    classroom_process_creator.remove_user(user1.UserId)
    classroom_process_creator.remove_user(user2.UserId)

    classroom_process_creator.stop()

    assert len([class_dir for class_dir in tmp_path.iterdir()]) == 0
    assert not classroom_process_creator.IsRunning
    assert classroom_process_creator.NumOfProcesses == 0
