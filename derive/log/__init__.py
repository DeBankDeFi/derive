import io
import logging
import os
import os.path
import sys
import traceback
import typing
from logging import (
    CRITICAL,
    FATAL,
    ERROR,
    WARN,
    WARNING,
    INFO,
    DEBUG,
    NOTSET,
    Logger,
)
from types import FrameType

from derive.log.formatter import DatetimeFormatter
from derive.log.record import DeriveLogRecord
from derive.log.types import ArgsType, SysExcInfoType

__all__ = [
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "FATAL",
    "INFO",
    "NOTSET",
    "WARN",
    "WARNING",
    "critical",
    "debug",
    "error",
    "exception",
    "fatal",
    "getLogger",
    "info",
    "log",
    "warning",
    "DeriveLogger",
    "DeriveLogRecord",
    "stderr_stream_handler",
]


class DeriveLogger(logging.Logger):
    _f = lambda: None
    _srcfile = os.path.normcase(_f.__code__.co_filename)

    def makeRecord(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: object,
        args: ArgsType,
        exc_info: typing.Optional[SysExcInfoType] = None,
        func: typing.Optional[str] = None,
        extra: typing.Optional[typing.Mapping[str, object]] = None,
        sinfo: typing.Optional[str] = None,
    ) -> DeriveLogRecord:
        rv = DeriveLogRecord(
            name, level, fn, lno, msg, args, exc_info, func, sinfo, extra
        )
        return rv

    def findCaller(
        self, stack_info: bool = False, stacklevel: int = 1
    ) -> typing.Tuple[str, int, str, typing.Optional[str]]:
        f = self.current_frame()
        if f is not None:
            f = f.f_back  # type: ignore[assignment]
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == self._srcfile:
                f = f.f_back  # type: ignore[assignment]
                continue
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write("Stack (most recent call last):\n")
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == "\n":
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)  # type: ignore[assignment]
            break
        return rv

    @staticmethod
    def current_frame() -> FrameType:
        return sys._getframe(4)


stderr_stream_handler = logging.StreamHandler(sys.stderr)
stderr_stream_handler.setFormatter(DatetimeFormatter())

root = DeriveLogger("root", logging.INFO)
root.addHandler(stderr_stream_handler)
manager = logging.Manager(typing.cast(logging.RootLogger, root))
manager.loggerClass = DeriveLogger


def getLogger(name: str = "") -> Logger:
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    if name:
        return manager.getLogger(name)
    else:
        return root


def critical(
    msg,
    *args,
    stack_info: bool = False,
    extra: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    **kwargs,
):
    root.critical(msg, *args, extra=extra, stack_info=stack_info, **kwargs)


fatal = critical


def error(
    msg,
    *args,
    stack_info: bool = False,
    extra: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    **kwargs,
):
    root.error(msg, *args, extra=extra, stack_info=stack_info, **kwargs)


def exception(
    msg,
    *args,
    exc_info=True,
    stack_info: bool = False,
    extra: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    **kwargs,
):
    root.error(
        msg, *args, stack_info=stack_info, exc_info=exc_info, extra=extra, **kwargs
    )


def warning(
    msg,
    *args,
    stack_info: bool = False,
    extra: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    **kwargs,
):
    root.warning(msg, *args, extra=extra, stack_info=stack_info, **kwargs)


def info(
    msg,
    *args,
    stack_info: bool = False,
    extra: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    **kwargs,
):
    root.info(msg, *args, extra=extra, stack_info=stack_info, **kwargs)


def debug(
    msg,
    *args,
    stack_info: bool = False,
    extra: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    **kwargs,
):
    root.debug(msg, *args, extra=extra, stack_info=stack_info, **kwargs)


def log(
    level: int,
    msg,
    *args,
    stack_info: bool = False,
    extra: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    **kwargs,
):
    root.log(level, msg, *args, extra=extra, stack_info=stack_info, **kwargs)
