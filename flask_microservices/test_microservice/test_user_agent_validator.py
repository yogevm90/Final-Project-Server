class TestUserAgentValidator(object):
    NOT_ALLOWED = ["windows", "mac", "linux", "chromeos", "cros", "win"]

    @staticmethod
    def validate(user_agent):
        for invalid_user_agent in TestUserAgentValidator.NOT_ALLOWED:
            if invalid_user_agent in user_agent:
                return False
            if user_agent in invalid_user_agent:
                return False
        return True
