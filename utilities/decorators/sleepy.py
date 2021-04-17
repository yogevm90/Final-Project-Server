from time import time, sleep


class Sleepy(object):
    """
    Decorator for executing a function in a predefined time
    """
    def __init__(self, function, timeout=5):
        """
        :param function: function to execute
        :param timeout: time to execute function
        """
        self._func = function
        self._timeout = timeout
        self._total_heavy_timed_tasks = [timeout]

    def __call__(self, *args, **kwargs):
        """
        Wrapper for running in specific time

        :param args: arguments for execution
        :param kwargs: kwargs for execution
        :return: result of function if there is any
        """
        start = time()

        result = self._func(*args, **kwargs)

        end = time()
        elapsed = end - start

        if elapsed > self._timeout:
            self._total_heavy_timed_tasks += [elapsed]
            self._timeout = sum(self._total_heavy_timed_tasks) / len(self._total_heavy_timed_tasks)

        to_wait = self._timeout - elapsed

        if elapsed > 0:
            sleep(to_wait)

        return result
