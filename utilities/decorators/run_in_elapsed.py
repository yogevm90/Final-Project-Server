from time import time


def run_in_elapsed(func):

    def wrapper(*args, **kwargs):
        start = time()

        res = func(*args, **kwargs)

        print(f"Elapsed: {time() - start}")
        return res

    return wrapper
