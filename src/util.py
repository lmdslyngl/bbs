
import logging
from logging import StreamHandler
from logging.handlers import SysLogHandler
import inspect
import conf


def init_root_logger() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s")

    handler_stderr = StreamHandler()
    handler_stderr.setFormatter(formatter)
    logger.addHandler(handler_stderr)

    if conf.syslog_enabled:
        handler_syslog = SysLogHandler(
            address=(conf.syslog_host, conf.syslog_port),
            facility=SysLogHandler.LOG_USER)
        handler_syslog.setFormatter(formatter)
        logger.addHandler(handler_syslog)


def get_current_logger() -> logging.Logger:
    func_name = inspect.stack()[0][3]
    return logging.getLogger(func_name)
