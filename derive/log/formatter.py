import logging
import time
import typing
from logging import Formatter


class DatetimeFormatter(Formatter):
    default_time_format = "%Y-%m-%d %H:%M:%S"
    default_msec_format = "%s.%03d"

    def __init__(self, fmt: str = "[%(asctime)s] %(levelname)s: %(name)s: %(message)s"):
        super().__init__(fmt)

    def formatTime(
        self, record: logging.LogRecord, datefmt: typing.Optional[str] = None
    ) -> str:
        ct = self.converter(record.created)  # type: ignore[call-arg, misc]
        t = time.strftime(self.default_time_format, ct)
        s = self.default_msec_format % (t, record.msecs)
        return s

    def usesTime(self):
        return True
