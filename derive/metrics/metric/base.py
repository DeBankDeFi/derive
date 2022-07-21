from __future__ import annotations

import math
import typing
from dataclasses import dataclass
from multiprocessing.managers import BaseProxy, SyncManager
from typing import Union, Iterable, Mapping, Optional, Sequence

from derive.metrics.collector import GlobalCollector
from derive.metrics.context_manger import InprogressTracker, Timer, ExceptionCounter

INF = float("inf")
MINUS_INF = float("-inf")
NaN = float("NaN")


def float_to_string(d: float) -> str:
    d = float(d)
    if d == INF:
        return "+Inf"
    elif d == MINUS_INF:
        return "-Inf"
    elif math.isnan(d):
        return "NaN"
    else:
        s = repr(d)
        dot = s.find(".")
        # Go switches to exponents sooner than Python.
        # We only need to care about positive values for le/quantile.
        if d > 0 and dot > 6:
            mantissa = "{0}.{1}{2}".format(s[0], s[1:dot], s[dot + 1 :]).rstrip("0.")
            return "{0}e+0{1}".format(mantissa, dot - 1)
        return s


class MetricValue:
    def __init__(self, value=0.0):
        self._value = value

    def inc(self, amount: Union[float, int]):
        self._value += amount

    def set(self, value: Union[float, int]):
        self._value = value

    def get(self) -> float:
        return self._value

    value = property(get, set)


class MetricValueProxy(BaseProxy):
    _exposed_ = ("get", "set", "inc")

    def inc(self, amount: Union[float, int]):
        self._callmethod("inc", (amount,))

    def get(self) -> float:
        return self._callmethod("get")  # type: ignore[func-returns-value]

    def set(self, value: Union[float, int]):
        self._callmethod("set", (value,))

    value = property(get, set)


@dataclass
class Sample:
    name: str
    labels: Mapping[str, str]
    value: float

    def data(self) -> str:
        if self.labels:
            label = "{{{0}}}".format(
                ",".join([f'{k}="{v}"' for k, v in sorted(self.labels.items())])
            )
        else:
            label = ""
        return f"{self.name}{label} {float_to_string(self.value)}"


class Metric(metaclass=GlobalCollector):
    _type: str

    def __init__(
        self,
        name: str,
        document: str,
        labels: Optional[Mapping[str, str]] = None,
    ):
        self.name = name
        if labels:
            self.identity = self.name + "{{{0}}}".format(
                ",".join([f'{k}="{v}"' for k, v in sorted(labels.items())])
            )
            self._labels = labels
        else:
            self.identity = self.name
            self._labels = {}
        self.document = document.replace("\\", r"\\").replace("\n", r"\n")

    def help(self) -> str:
        return f"# HELP {self.name} {self.document}"

    def type(self) -> str:
        return f"# TYPE {self.name} {self._type}"

    def samples(self) -> Iterable[Sample]:
        yield from []

    def export(self) -> Iterable[str]:
        yield self.help()
        yield self.type()
        for sample in self.samples():
            yield sample.data()

    def init(self, m: SyncManager):
        pass


class Counter(Metric):
    _type = "counter"
    _count: MetricValue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def inc(self, mount: Union[float, int] = 1):
        self._count.inc(mount)

    def help(self) -> str:
        return f"# HELP {self.name}_total {self.document}"

    def type(self) -> str:
        return f"# TYPE {self.name}_total {self._type}"

    def samples(self) -> Iterable[Sample]:
        yield Sample(
            name=f"{self.name}_total", labels=self._labels, value=self._count.get()
        )

    def count_exceptions(self, exception=Exception):
        """Count exceptions in a block of code or function.

        Can be used as a function decorator or context manager.
        Increments the counter when an exception of the given
        type is raised up out of the code.
        """
        return ExceptionCounter(self, exception)

    def init(self, m: SyncManager):
        self._count = getattr(m, "MetricValue")()


class Gauge(Counter):
    _type = "gauge"

    def dec(self, amount: Union[float, int] = 1):
        """Decrement gauge by the given amount."""
        self._count.inc(-amount)

    def set(self, value: Union[float, int]):
        """Set gauge to the given value."""
        self._count.set(value)

    def track_inprogress(self):
        """Track inprogress blocks of code or functions.

        Can be used as a function decorator or context manager.
        Increments the gauge when the code is entered,
        and decrements when it is exited.
        """
        return InprogressTracker(self)

    def time(self):
        """Time a block of code or function, and set the duration in seconds.

        Can be used as a function decorator or context manager.
        """
        return Timer(self.set)

    def help(self) -> str:
        return f"# HELP {self.name} {self.document}"

    def type(self) -> str:
        return f"# TYPE {self.name} {self._type}"

    def samples(self) -> Iterable[Sample]:
        yield Sample(name=self.name, labels=self._labels, value=self._count.get())


class Summary(Metric):

    _type = "summary"
    _count: MetricValue
    _sum: MetricValue

    def observe(self, amount):
        """Observe the given amount."""
        self._count.inc(1)
        self._sum.inc(amount)

    def time(self):
        """Time a block of code or function, and observe the duration in seconds.

        Can be used as a function decorator or context manager.
        """
        return Timer(self.observe)

    def help(self) -> str:
        return f"# HELP {self.name} {self.document}"

    def type(self) -> str:
        return f"# TYPE {self.name} {self._type}"

    def samples(self) -> Iterable[Sample]:
        yield Sample(
            name=f"{self.name}_count", labels=self._labels, value=self._count.get()
        )
        yield Sample(
            name=f"{self.name}_sum", labels=self._labels, value=self._sum.get()
        )

    def init(self, m: SyncManager):
        self._count = getattr(m, "MetricValue")()
        self._sum = getattr(m, "MetricValue")()


class Histogram(Metric):
    _type = "histogram"
    DEFAULT_BUCKETS: typing.Tuple[float, ...] = (
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
        INF,
    )
    _buckets: Sequence[MetricValue]
    _sum: MetricValue

    def __init__(self, *args, buckets=DEFAULT_BUCKETS, **kwargs):
        super().__init__(*args, **kwargs)
        buckets = [float(b) for b in buckets]
        if buckets != sorted(buckets):
            # This is probably an error on the part of the user,
            # so raise rather than sorting for them.
            raise ValueError("Buckets not in sorted order")
        if buckets and buckets[-1] != INF:
            buckets.append(INF)
        if len(buckets) < 2:
            raise ValueError("Must have at least two buckets")
        self._upper_bounds = buckets

    def observe(self, amount: float):
        """Observe the given amount."""
        self._sum.inc(amount)
        for i, bound in enumerate(self._upper_bounds):
            if amount <= bound:
                self._buckets[i].inc(1)
                break

    def time(self):
        """Time a block of code or function, and observe the duration in seconds.

        Can be used as a function decorator or context manager.
        """
        return Timer(self.observe)

    def help(self) -> str:
        return f"# HELP {self.name} {self.document}"

    def type(self) -> str:
        return f"# TYPE {self.name} {self._type}"

    def samples(self) -> Iterable[Sample]:
        acc = 0.0
        for i, bound in enumerate(self._upper_bounds):
            acc += self._buckets[i].get()

            yield Sample(
                name=f"{self.name}_bucket",
                labels={**self._labels, "le": float_to_string(bound)},
                value=acc,
            )
        yield Sample(name=f"{self.name}_count", labels={}, value=acc)
        if self._upper_bounds[0] >= 0:
            yield Sample(name=f"{self.name}_sum", labels={}, value=self._sum.get())

    def init(self, m: SyncManager):
        self._buckets = [getattr(m, "MetricValue")() for _ in self._upper_bounds]
        self._sum = getattr(m, "MetricValue")()
