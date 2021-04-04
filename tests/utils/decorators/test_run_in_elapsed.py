import time
from unittest import mock

from utilities.decorators.run_in_elapsed import run_in_elapsed


@mock.patch("time.sleep")
def test_run_in_elapsed(mock_sleep):
    """
    Test that run_in_elapsed doesn't break the flow of the function

    :param mock_sleep: mock for time.sleep
    """
    @run_in_elapsed
    def f():
        time.sleep(5)

    f()

    mock_sleep.assert_called()
