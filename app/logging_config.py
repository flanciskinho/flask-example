import logging
import logging.config
import os
from pythonjsonlogger import jsonlogger

from .logging_filters import RequestIdFilter


class DefaultingFormatter(jsonlogger.JsonFormatter):
    """
    Garantiza que todos los registros tengan los campos esperados,
    aunque falten, para evitar KeyError.
    """
    def format(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return super().format(record)


def setup_logging(env: str = None):
    """
    Configura logging para Flask + Gunicorn.

    Args:
        env (str): 'development' o 'production'. Se autodetecta si no se pasa.
    """
    env = env or os.getenv("FLASK_ENV", "production")
    is_dev = env == "development"

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,

        # ── FILTROS ──
        "filters": {
            "request_id": {
                "()": RequestIdFilter,  # Solo para logs Flask
            }
        },

        # ── FORMATTERS ──
        "formatters": {
            "dev": {
                "format": "[%(levelname)s] %(asctime)s - %(name)s [request_id=%(request_id)s] - %(message)s"
            },
            "json": {
                "()": DefaultingFormatter,
                "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
            },
        },

        # ── HANDLERS ──
        "handlers": {
            "console": {  # Logs de Flask
                "class": "logging.StreamHandler",
                "formatter": "dev" if is_dev else "json",
                "filters": ["request_id"],
                "stream": "ext://sys.stdout",
            },
            "gunicorn_console": {  # Logs de Gunicorn
                "class": "logging.StreamHandler",
                "formatter": "dev" if is_dev else "json",
                "stream": "ext://sys.stdout",
            },
        },

        # ── LOGGERS ──
        "loggers": {
            # Logs de Gunicorn
            "gunicorn.error": {
                "handlers": ["gunicorn_console"],
                "level": "INFO",
                "propagate": False,
            },
            "gunicorn.access": {
                "handlers": ["gunicorn_console"],
                "level": "INFO",
                "propagate": False,
            },
        },

        # ── ROOT LOGGER ──
        "root": {
            "handlers": ["console"],
            "level": "DEBUG" if is_dev else "INFO",
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
