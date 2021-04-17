from time import time


def run_in_elapsed(func):
    """
    Module to run commands and check how much time it took

    :param func: func to run
    :return: wrapper for running in elapse
    """

    def wrapper(*args, **kwargs):
        """
        Wrap func to execute and check how much time elapsed for the execution of func

        :param args: arguments for func
        :param kwargs: kwargs for func
        :return: result of func if there is any
        """
        start = time()

        res = func(*args, **kwargs)

        print(f"Elapsed: {time() - start}")
        return res

    return wrapper
