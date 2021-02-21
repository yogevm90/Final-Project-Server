from unittest import mock

import pytest

from server.classroom_manager.process_creators.video_data_receiver import VideoDataReceiver


@pytest.fixture(autouse=True)
def student_path_mock(tmp_path):
    for i in range(100):
        video_mock = tmp_path / str(i)
        video_mock.touch()
        video_mock.write_text(f"{i}")

    yield tmp_path

    # Clean if needed
    for i in range(100):
        video_mock = tmp_path / str(i)
        if video_mock.is_file():
            video_mock.unlink()


@mock.patch("server.classroom_manager.process_creators.video_data_receiver.VideoReader")
def test_video_data_receiver_full_flow(video_reader_mock, student_path_mock, tmp_path):
    """
    Test that the VideoDataReceiver reads and cleans the path.

    :param video_reader_mock: mock for VideoReader
    :param student_path_mock: mock path to a student folder
    :param tmp_path: pytest tmp_path
    """
    video_data_receiver = VideoDataReceiver(str(tmp_path))
    video_reader_mock("mock").read.side_effect = [i for i in range(100)]

    data_list = [video_data_receiver.receive_data() for _ in range(100)]

    assert data_list == [i for i in range(100)], "Didn't get all of the data from the files"
    assert [(tmp_path / str(i)).is_file() for i in range(100)] == [], "Didn't clear all videos from folder"
