import inspect
import types as python_types
import typing
from functools import wraps
from typing import Callable, Any

from opentelemetry import trace as opentelemetry_trace
from opentelemetry.trace.span import SpanContext, Span
from opentelemetry.util import types

_tracer = opentelemetry_trace.get_tracer(__name__)


def set_provider(provider: opentelemetry_trace.TracerProvider) -> None:
    opentelemetry_trace.set_tracer_provider(provider)
    global _tracer
    _tracer = provider.get_tracer(__name__)


def get_provider() -> opentelemetry_trace.TracerProvider:
    return opentelemetry_trace.get_tracer_provider()


def get_tracer() -> opentelemetry_trace.Tracer:
    return _tracer


class trace:
    """
    example::
        >>> @trace("function")
        ... def function():
        ...     trace.set_attribute("type", "function")
        >>> with trace("test") as span:
        ...     span.set_attribute("type", "context")
        >>> @trace("function")
        ... async def function():
        ...     trace.set_attribute("type", "coroutine")
    """

    @staticmethod
    def get_current_span() -> typing.Optional[Span]:
        span = opentelemetry_trace.get_current_span()
        if span is opentelemetry_trace.INVALID_SPAN:
            return None
        return span

    @classmethod
    def get_current_span_context(cls) -> typing.Optional[SpanContext]:
        span = cls.get_current_span()
        if span is not None:
            return span.get_span_context()
        return None

    @staticmethod
    def set_attribute(key: str, value: types.AttributeValue) -> None:
        opentelemetry_trace.get_current_span().set_attribute(key, value)

    def __init__(self, operation: str):
        self.operation = operation

    def _recreate_cm(self) -> "trace":
        return self.__class__(operation=self.operation)

    def __enter__(self) -> Span:
        self.local_span = _tracer.start_as_current_span(self.operation)
        return self.local_span.__enter__()  # type: ignore[no-any-return]

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[python_types.TracebackType],
    ):
        return self.local_span.__exit__(exc_type, exc_val, exc_tb)  # type: ignore[return-value]

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def inner(*args, **kwds):  # type: ignore[no-untyped-def]
                with self._recreate_cm():
                    return await func(*args, **kwds)

        else:

            @wraps(func)
            def inner(*args, **kwds):  # type: ignore[no-untyped-def]
                with self._recreate_cm():
                    return func(*args, **kwds)

        return inner
