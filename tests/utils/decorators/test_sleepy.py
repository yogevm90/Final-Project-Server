from unittest import mock

from utilities.decorators.sleepy import Sleepy

from time import sleep


def test_sleepy_sleep_called():
    """
    Test that sleepy calls sleep if needed
    """
    @Sleepy
    def f():
        sleep(0.25)

    with mock.patch("utilities.decorators.sleepy.sleep") as mock_sleep:
        f()
        mock_sleep.assert_called()


def test_sleepy_sleep_not_called():
    """
    Test that sleepy calls sleep if needed
    """
    @Sleepy
    def f():
        pass

    with mock.patch("utilities.decorators.sleepy.sleep") as mock_sleep:
        f()
        mock_sleep.assert_not_called()
