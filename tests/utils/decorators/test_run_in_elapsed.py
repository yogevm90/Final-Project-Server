from time import sleep

from utilities.decorators.run_in_elapsed import run_in_elapsed


def test_run_in_elapsed():
    @run_in_elapsed
    def f():
        sleep(5)

    f()
