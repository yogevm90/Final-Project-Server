from unittest import mock

import pytest

from server.classroom_manager.classroom.classroom_config import ClassroomConfig
from server.classroom_manager.managers.classroom_process_creators_manger import ClassroomProcessCreatorsManager


@pytest.fixture
def mock_classroom_config():
    classroom_id = "class_mock"
    user_ids = [f"u{i}" for i in range(50)]
    working_dir = "mock/dir"
    return ClassroomConfig(classroom_id=classroom_id, user_ids=user_ids, working_dir=working_dir)


@mock.patch("server.classroom_manager.managers.classroom_process_creators_manger.ClassroomProcessCreator")
def test_classroom_process_creators_manager_regular_flow(classroom_process_creator, mock_classroom_config):
    ClassroomProcessCreatorsManager.manage(mock_classroom_config)
