import subprocess

from server.stream_manager.exceptions import StreamUserException


def add_user(username, password):
    completed_proc = subprocess.run('sudo scripts/add_user.sh {} {}'.format(username, password))
    if completed_proc.returncode != 0:
        raise StreamUserException('failed to add user {} to the stream server'.format(username))


def change_password(username, password):
    completed_proc = subprocess.run('sudo scripts/change_password.sh {} {}'.format(username, password))
    if completed_proc.returncode != 0:
        raise StreamUserException('failed to change password to user {} on stream server'.format(username))
