from unittest import mock
from unittest.mock import MagicMock

from flask_microservices.test_microservice.test_app import TestApp
from flask_microservices.test_microservice.test_user_agent_validator import TestUserAgentValidator


def render_template_mock(html_file, msg="", *args, **kwargs):
    if msg:
        return html_file, msg
    return html_file


def set_render_template_mock(flask_mock: MagicMock):
    flask_mock.render_template = render_template_mock


@mock.patch("flask_microservices.test_microservice.test_app.flask")
def test_test_app_actual_start_test_valid_data(flask_mock):
    set_render_template_mock(flask_mock)
    app = TestApp("mock")
    result = app.actual_start_test()

    assert result == "qr_code_page.html"


@mock.patch("flask_microservices.test_microservice.test_app.flask")
@mock.patch("flask_microservices.test_microservice.test_app.TestApp._data_is_valid", return_value=False)
def test_test_app_actual_start_test_invalid_data(mock_data_is_valid, flask_mock):
    set_render_template_mock(flask_mock)
    app = TestApp("mock")
    result = app.actual_start_test()

    assert result == "verification_page.html"
    mock_data_is_valid.assert_called()


@mock.patch("flask_microservices.test_microservice.test_app.flask")
@mock.patch("flask_microservices.test_microservice.test_app.uuid")
@mock.patch("flask_microservices.test_microservice.test_app.TestApp._data_is_valid", return_value=True)
def test_test_app_actual_verify_correct_ver_id(mock_data_is_valid, mock_uuid, flask_mock):
    set_render_template_mock(flask_mock)
    mock_uuid.uuid4.return_value = "1234"
    mock_uuid.uuid5.return_value = "12345"
    flask_mock.request.user_agent.platform = "MockOS"
    app = TestApp("mock")

    app.actual_start_test()
    result = app.actual_verify(test_id="12345", verification_id="1234")

    assert type(result) == str, "The result contains a message, hence it detected a failure"
    assert result == "verification_page.html"
    mock_data_is_valid.assert_called()
    mock_uuid.uuid4.assert_called()
    mock_uuid.uuid5.assert_called()


@mock.patch("flask_microservices.test_microservice.test_app.flask")
@mock.patch("flask_microservices.test_microservice.test_app.uuid")
@mock.patch("flask_microservices.test_microservice.test_app.TestApp._data_is_valid", return_value=True)
def test_test_app_actual_verify_not_correct_ver_id(mock_data_is_valid, mock_uuid, flask_mock):
    set_render_template_mock(flask_mock)
    mock_uuid.uuid4.return_value = "1234"
    mock_uuid.uuid5.return_value = "12345"
    flask_mock.request.user_agent.platform = "MockOS"
    app = TestApp("mock")

    app.actual_start_test()
    result = app.actual_verify(test_id="12345", verification_id="1235")

    assert type(result) == tuple, "The result contains doesn't message, hence it didn't detect a failure"

    html_page, msg = result

    assert html_page == "verification_page.html"
    assert msg == "Invalid ID inserted!\n"
    mock_data_is_valid.assert_called()
    mock_uuid.uuid4.assert_called()
    mock_uuid.uuid5.assert_called()


@mock.patch("flask_microservices.test_microservice.test_app.flask")
@mock.patch("flask_microservices.test_microservice.test_app.uuid")
@mock.patch("flask_microservices.test_microservice.test_app.TestApp._data_is_valid", return_value=True)
def test_test_app_actual_verify_not_valid_platforms(mock_data_is_valid, mock_uuid, flask_mock):
    set_render_template_mock(flask_mock)
    mock_uuid.uuid4.return_value = "1234"
    mock_uuid.uuid5.return_value = "12345"
    app = TestApp("mock")

    for not_valid_platform in TestUserAgentValidator.NOT_ALLOWED:
        flask_mock.request.user_agent.platform = not_valid_platform
        app.actual_start_test()
        result = app.actual_verify(test_id="12345", verification_id="1234")

        assert type(result) == tuple, "The result contains doesn't message, hence it didn't detect a failure"

        html_page, msg = result

        assert html_page == "verification_page.html"
        assert msg == "Next time you try to insert the ID from your PC you will fail the test :)"
        mock_data_is_valid.assert_called()
        mock_uuid.uuid4.assert_called()
        mock_uuid.uuid5.assert_called()
