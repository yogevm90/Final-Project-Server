class TestUserAgentValidator(object):
    """
    Object to verify if the User Agent for verifying the test is valid
    """
    NOT_ALLOWED = ["windows", "mac", "linux", "chromeos", "cros", "win"]

    @staticmethod
    def validate(user_agent):
        """
        Validate if the user agent is valid

        :param user_agent: user agent
        :return: True if it is valid
        """
        for invalid_user_agent in TestUserAgentValidator.NOT_ALLOWED:
            if invalid_user_agent in user_agent:
                return False
            if user_agent in invalid_user_agent:
                return False
        return True
