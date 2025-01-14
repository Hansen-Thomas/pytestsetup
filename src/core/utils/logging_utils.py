from functools import wraps
import json
import logging
import logging.config
import os
import sys
import traceback

logger = logging.getLogger("method_logger")


def setup_logging(
    default_level=logging.INFO,
) -> None:
    # create local logging-directories if not exist:
    paths = [
        "logs",
    ]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)

    # load logging-config:
    LOGGING_CONFIG_PATH = "src/app/logging.json"
    if os.path.exists(LOGGING_CONFIG_PATH):
        with open(LOGGING_CONFIG_PATH, "rt") as f:
            config = json.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def global_exception_hook(type, value, traceback_obj):
    """Used to log unhandled exceptions before the app crashes."""

    error_msg = "".join(traceback.format_exception(type, value, traceback_obj))
    logger = logging.getLogger(__name__)
    logger.error(f"unhandled Exception: {error_msg},")
    logger.info("--- CLOSE APP AFTER UNHANDLED EXCEPTION -------------------")
    sys.exit(1)


def log_method(func):
    """Decorator to log method-calls and return-values."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Log the method name
        logger.info(f"Calling method: {func.__name__}")

        # Log the positional and keyword arguments
        logger.info(f"Arguments: {args if args else 'None'}")
        logger.info(f"Keyword arguments: {kwargs if kwargs else 'None'}")

        # Call the original function
        result = func(*args, **kwargs)

        # Log the return value
        logger.info(f"Return value: {result}")
        return result

    return wrapper
