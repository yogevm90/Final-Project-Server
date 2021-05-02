import os

from server.stream_manager.exceptions import StreamUserException


def add_user(username, password):
    current_dir = os.path.dirname(__file__)
    return_code = os.system('bash {}/scripts/add_user.sh {} {}'.format(current_dir, username, password))
    if return_code != 0:
        raise StreamUserException('Failed to add user {} to stream server'.format(username))


def change_password(username, password):
    current_dir = os.path.dirname(__file__)
    return_code = os.system('bash {}/scripts/change_password.sh {} {}'.format(current_dir, username, password))
    if return_code != 0:
        raise StreamUserException('failed to change password to user {} on stream server'.format(username))
