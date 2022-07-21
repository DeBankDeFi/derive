import typing
from typing import overload, Set, Optional, Tuple

from derive.metrics.metric import base
from derive.metrics.metric import label


class Counter:
    """
    Example use cases for Counters:
    - Number of requests processed
    - Number of items that were inserted into a queue
    - Total amount of data that a system has processed

    Counters can only go up (and be reset when the process restarts). If your use case can go down,
    you should use a Gauge instead.

    An example for a Counter:

        from derive.metrics import Counter

        c = Counter('my_failures_total', 'Description of counter')
        c.inc()     # Increment by 1
        c.inc(1.6)  # Increment by given value

    There are utilities to count exceptions raised:

        @c.count_exceptions()
        def f():
            pass

        with c.count_exceptions():
            pass

        # Count only one type of exception
        with c.count_exceptions(ValueError):
            pass
    """

    @overload
    def __new__(cls, name: str, document: str, labels: Set[str]) -> label.Counter:  # type: ignore[misc]
        ...

    @overload
    def __new__(cls, name: str, document: str) -> base.Counter:  # type: ignore[misc]
        ...

    def __new__(cls, name: str, document: str, labels: Optional[Set[str]] = None):
        if labels:
            return label.Counter(name, document, labels)
        else:
            return base.Counter(name, document)


class Summary:
    """
    A Summary tracks the size and number of events.

    Example use cases for Summaries:
    - Response latency
    - Request size

    Example for a Summary:

        from derive.metrics import Summary

        s = Summary('request_size_bytes', 'Request size (bytes)')
        s.observe(512)  # Observe 512 (bytes)

    Example for a Summary using time:

        from derive.metrics import Summary

        REQUEST_TIME = Summary('response_latency_seconds', 'Response latency (seconds)')

        @REQUEST_TIME.time()
        def create_response(request):
          '''A dummy function'''
          time.sleep(1)

    Example for using the same Summary object as a context manager:

        with REQUEST_TIME.time():
            pass  # Logic to be timed
    """

    @overload
    def __new__(cls, name: str, document: str, labels: Set[str]) -> label.Summary:  # type: ignore[misc]
        ...

    @overload
    def __new__(cls, name: str, document: str) -> base.Summary:  # type: ignore[misc]
        ...

    def __new__(cls, name: str, document: str, labels: Optional[Set[str]] = None):
        if labels:
            return label.Summary(name, document, labels)
        else:
            return base.Summary(name, document)


class Gauge:
    """
    Gauge metric, to report instantaneous values.

     Examples of Gauges include:
        - Inprogress requests
        - Number of items in a queue
        - Free memory
        - Total memory
        - Temperature

     Gauges can go both up and down.

        from derive.metrics import Gauge

        g = Gauge('my_inprogress_requests', 'Description of gauge')
        g.inc()      # Increment by 1
        g.dec(10)    # Decrement by given value
        g.set(4.2)   # Set to a given value

    There are utilities for common use cases:

        # Increment when entered, decrement when exited.
        @g.track_inprogress()
        def f():
            pass

        with g.track_inprogress():
            pass
    """

    @overload
    def __new__(cls, name: str, document: str, labels: Set[str]) -> label.Gauge:  # type: ignore[misc]
        ...

    @overload
    def __new__(cls, name: str, document: str) -> base.Gauge:  # type: ignore[misc]
        ...

    def __new__(cls, name: str, document: str, labels: Optional[Set[str]] = None):
        if labels:
            return label.Gauge(name, document, labels)
        else:
            return base.Gauge(name, document)


class Histogram:
    """
    A Histogram tracks the size and number of events in buckets.

    You can use Histograms for aggregatable calculation of quantiles.

    Example use cases:
    - Response latency
    - Request size

    Example for a Histogram:

        from derive.metrics import Histogram

        h = Histogram('request_size_bytes_histogram', 'Request size (bytes)')
        h.observe(512)  # Observe 512 (bytes)
    """

    @overload
    def __new__(  # type: ignore[misc]
        cls,
        name: str,
        document: str,
        labels: Set[str],
        *,
        buckets: Tuple[float, ...] = base.Histogram.DEFAULT_BUCKETS
    ) -> label.Histogram:
        ...

    @overload
    def __new__(  # type: ignore[misc]
        cls,
        name: str,
        document: str,
        *,
        buckets: Tuple[float, ...] = base.Histogram.DEFAULT_BUCKETS
    ) -> base.Histogram:
        ...

    def __new__(
        cls,
        name: str,
        document: str,
        labels: Optional[Set[str]] = None,
        *,
        buckets: Tuple[float, ...] = base.Histogram.DEFAULT_BUCKETS
    ):
        if labels:
            return label.Histogram(name, document, labels, buckets=buckets)
        else:
            return base.Histogram(name, document, buckets=buckets)
