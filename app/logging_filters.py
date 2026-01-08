import logging
from flask import g, has_request_context


class RequestIdFilter(logging.Filter):
    """
    Inyecta request_id en cada log record si hay contexto Flask.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if has_request_context():
            record.request_id = getattr(g, "request_id", "-")
        else:
            record.request_id = "-"

        return True
