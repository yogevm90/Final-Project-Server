from flask_microservices.test_microservice.test_user_agent_validator import TestUserAgentValidator


def test_test_user_agent_validator_valid():
    result = TestUserAgentValidator.validate("mock")

    assert result


def test_test_user_agent_validator_invalid():
    for invalid in TestUserAgentValidator.NOT_ALLOWED:
        result = TestUserAgentValidator.validate(invalid)

        assert not result
