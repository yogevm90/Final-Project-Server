from time import time, sleep


class Sleepy(object):
    """
    Decorator
    """
    def __init__(self, function, timeout=5):
        self._func = function
        self._timeout = timeout
        self._total_heavy_timed_tasks = [timeout]

    def __call__(self, *args, **kwargs):
        start = time()

        self._func(*args, **kwargs)

        end = time()
        elapsed = end - start

        if elapsed > self._timeout:
            self._total_heavy_timed_tasks += [elapsed]
            self._timeout = sum(self._total_heavy_timed_tasks) / len(self._total_heavy_timed_tasks)

        to_wait = self._timeout - elapsed

        if elapsed > 0:
            sleep(to_wait)
