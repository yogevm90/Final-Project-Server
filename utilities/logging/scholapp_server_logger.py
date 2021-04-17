import logging
import os
from datetime import datetime
from pathlib import Path


class ScholappLogger(object):
    """
    A class to represent the logging mechanism
    """

    _LOGGER = logging.getLogger("Scholapp")

    @staticmethod
    def init_logger(logs_name, create_time_folder=False):
        """
        Initialize the logger

        :param logs_name: path to logs path
        :param create_time_folder: create a folder by time
        :return: logs path
        """
        import logging.config
        logs_path = ScholappLogger._get_logs_path(os.getcwd())
        if create_time_folder:
            today = datetime.today().strftime("%d-%m-%Y_%H-%M-%S")
            logs_path = logs_path / today
            logs_path.mkdir()
        fh0 = logging.FileHandler(str(logs_path / logs_name))
        fh0.setLevel(logging.DEBUG)
        ScholappLogger._LOGGER.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s] [Scholapp server] [Process: %(process)d] [%(name)s] "
                                      "- %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
        ch.setFormatter(formatter)
        fh0.setFormatter(formatter)
        ScholappLogger._LOGGER.addHandler(fh0)
        ScholappLogger._LOGGER.addHandler(ch)
        return logs_path

    @staticmethod
    def info(msg, *args, **kwargs):
        """
        Run logging's info
        :param msg: msg to print
        :param args: arguments
        :param kwargs: kwargs
        :return: result of info
        """
        return ScholappLogger._LOGGER.info(msg, *args, **kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        """
        Run logging's debug
        :param msg: msg to print
        :param args: arguments
        :param kwargs: kwargs
        :return: result of debug
        """
        return ScholappLogger._LOGGER.debug(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        """
        Run logging's error
        :param msg: msg to print
        :param args: arguments
        :param kwargs: kwargs
        :return: result of error
        """
        return ScholappLogger._LOGGER.error(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        """
        Run logging's warning
        :param msg: msg to print
        :param args: arguments
        :param kwargs: kwargs
        :return: result of warning
        """
        return ScholappLogger._LOGGER.warning(msg, *args, **kwargs)

    @staticmethod
    def _get_logs_path(cwd) -> Path:
        cwd = Path(cwd)
        while "logs" not in [p.name for p in cwd.iterdir()]:
            cwd = cwd.parent
        return cwd / "logs"
