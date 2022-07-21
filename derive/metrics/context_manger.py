from __future__ import annotations
from contextlib import ContextDecorator
from time import perf_counter as default_timer
from typing import Type, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from derive.metrics.metric.base import Counter, Gauge


class ExceptionCounter(ContextDecorator):
    def __init__(self, counter: Counter, exception: Type[Exception]):
        self._counter = counter
        self._exception = exception

    def __enter__(self):
        pass

    def __exit__(self, typ, value, traceback):
        if isinstance(value, self._exception):
            self._counter.inc()


class InprogressTracker(ContextDecorator):
    def __init__(self, gauge: Gauge):
        self._gauge = gauge

    def __enter__(self):
        self._gauge.inc()

    def __exit__(self, typ, value, traceback):
        self._gauge.dec()


class Timer(ContextDecorator):
    def __init__(self, callback: Callable[[float], None]):
        self._callback = callback

    def _recreate_cm(self):
        return self.__class__(self._callback)

    def __enter__(self):
        self._start = default_timer()

    def __exit__(self, typ, value, traceback):
        # Time can go backwards.
        duration = max(default_timer() - self._start, 0)
        self._callback(duration)
