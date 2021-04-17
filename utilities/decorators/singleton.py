def singleton(cls):
    """
    Decorator for singleton

    :param cls: class object to make a singleton from
    :return: wrapper for singleton initialization
    """
    instances = {}

    def wrapper(*args, **kwargs):
        """
        Generate an instance of cls

        :param args: arguments for initialization
        :param kwargs: kwargs for initialization
        :return: instance of cls
        """
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
