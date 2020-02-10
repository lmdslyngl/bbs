
import logging
from logging import StreamHandler
from logging.handlers import SysLogHandler
import inspect


def init_root_logger() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s")

    handler_stderr = StreamHandler()
    handler_syslog = SysLogHandler(
        address=("127.0.0.1", 514),
        facility=logging.handlers.SysLogHandler.LOG_USER)

    handler_stderr.setFormatter(formatter)
    handler_syslog.setFormatter(formatter)

    logger.addHandler(handler_stderr)
    logger.addHandler(handler_syslog)


def get_current_logger() -> logging.Logger:
    func_name = inspect.stack()[0][3]
    return logging.getLogger(func_name)
