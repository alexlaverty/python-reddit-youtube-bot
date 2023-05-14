"""Default logging configuration, and associated utilities."""

from typing import Any, Dict

DEFAULT_LOG_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "propogate": False,
    "formatters": {
        "fmt": {
            "format": "%(asctime)s %(levelname)-8s %(message)s",
            "datefmt": "%d-%m-%Y %H:%M:%S",
        }
    },
    "handlers": {
        "fh": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "rybo.log",
            "maxBytes": 1048576,
            "backupCount": 3,
            "formatter": "fmt",
        },
        "sh": {
            "class": "logging.StreamHandler",
            "formatter": "fmt",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {"rybo": {"handlers": ["fh", "sh"], "level": "DEBUG"}},
}
