import logging
import typing

from derive.log.types import ArgsType, SysExcInfoType
from derive.trace import trace


class DeriveLogRecord(logging.LogRecord):
    trace_id: typing.Optional[str]
    attributes: typing.Dict[str, str]

    def __init__(
        self,
        name: str,
        level: int,
        pathname: str,
        lineno: int,
        msg: object,
        args: ArgsType,
        exc_info: typing.Optional[SysExcInfoType],
        func: typing.Optional[str] = None,
        sinfo: typing.Optional[str] = None,
        extra: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    ) -> None:
        super().__init__(
            name, level, pathname, lineno, msg, args, exc_info, func, sinfo
        )
        span_context = trace.get_current_span_context()
        if span_context is None:
            self.trace_id = None
        else:
            self.trace_id = f"{span_context.trace_id:032x}"
        self.attributes: typing.Mapping[str, str] = (
            {k: str(v) for k, v in extra.items()} if extra else {}
        )
