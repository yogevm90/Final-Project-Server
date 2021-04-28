import traceback

import flask

from utilities.logging.scholapp_server_logger import ScholappLogger


def in_try_catch(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            ScholappLogger.error(traceback.format_exc())
            return flask.jsonify({"verdict": False})

    return wrapper
