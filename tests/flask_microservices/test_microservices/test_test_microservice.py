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
    app = TestApp("mock", logs_name="mock")
    app._cookies[flask_mock.request.cookies.get("userID")] = "1234"
    result = app.actual_start_test("mock", "mock")

    assert result == "verification_page.html"


@mock.patch("flask_microservices.test_microservice.test_app.flask")
@mock.patch("flask_microservices.test_microservice.test_app.uuid")
def est_test_app_actual_verify_correct_ver_id(mock_uuid, flask_mock):
    set_render_template_mock(flask_mock)
    mock_uuid.uuid4.return_value = "1234"
    mock_uuid.uuid5.return_value = "12345"
    flask_mock.request.user_agent.platform = "MockOS"
    app = TestApp("mock", logs_name="mock")
    app._cookies[flask_mock.request.cookies.get("userID")] = "1234"

    app.actual_start_test("1234", "mock")
    result = app.actual_verify("mock", "1234")

    assert type(result) == str, "The result contains a message, hence it detected a failure"
    assert result == "verification_page.html"
    mock_uuid.uuid4.assert_called()
    mock_uuid.uuid5.assert_called()
