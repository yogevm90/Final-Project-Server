import logging
import os
from datetime import datetime
from pathlib import Path


class ScholappLogger(object):
    _LOGGER = logging.getLogger("Scholapp")

    @staticmethod
    def init_logger(logs_name, create_time_folder=False):
        import logging.config
        logs_path = ScholappLogger._get_logs_path(os.getcwd())
        if create_time_folder:
            today = datetime.today().strftime("%d-%m-%Y_%H-%M-%S")
            logs_path = logs_path / today
            logs_path.mkdir()
        fh = logging.FileHandler(str(logs_path / logs_name))
        fh.setLevel(logging.DEBUG)
        ScholappLogger._LOGGER.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s] [Scholapp server] [Process: %(process)d] [%(name)s] "
                                      "- %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        ScholappLogger._LOGGER.addHandler(ch)
        return logs_path

    @staticmethod
    def info(msg, *args, **kwargs):
        return ScholappLogger._LOGGER.info(msg, *args, **kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        return ScholappLogger._LOGGER.debug(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        return ScholappLogger._LOGGER.error(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        return ScholappLogger._LOGGER.warning(msg, *args, **kwargs)

    @staticmethod
    def _get_logs_path(cwd) -> Path:
        cwd = Path(cwd)
        while "logs" not in [p.name for p in cwd.iterdir()]:
            cwd = cwd.parent
        return cwd / "logs"
