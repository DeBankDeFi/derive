import logging
import typing

from derive.log.types import ArgsType, SysExcInfoType
from derive.trace import trace
import derive


class DeriveLogRecord(logging.LogRecord):
    BUILTIN_RECORD_ATTRS = frozenset(
        (
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "lineno",
            "module",
            "name",
            "pathname",
            "process",
            "processName",
            "thread",
            "threadName",
            "stack_info",
        )
    )
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

    def to_log_data(self) -> dict:
        # reference: https://opentelemetry.io/docs/reference/specification/logs/data-model/
        attributes: typing.Dict[str, str] = {}
        for attribute in self.BUILTIN_RECORD_ATTRS:
            attr_value = getattr(self, attribute)
            if attr_value:
                attributes[f"builtin_{attribute}"] = str(attr_value)

        data = {
            "SeverityText": self.levelname,
            "SeverityNumber": self.levelno,
            "Body": self.msg,
            "Timestamp": self.created,
            "Attributes": {**attributes, **self.attributes},
            "Resource": {
                k: str(v) for k, v in derive.get_global_resources().attributes.items()
            },
        }
        if getattr(self, "trace_id") is not None:
            data["TraceId"] = self.trace_id
        return data
