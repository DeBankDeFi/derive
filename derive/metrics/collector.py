from __future__ import annotations

from multiprocessing import Lock
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from derive.metrics.metric.base import Metric


class GlobalCollector(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._lock = Lock()

    def __call__(cls, *args, **kwargs):
        from derive.metrics.manager import metrics_mapping, manager

        m: Metric = super().__call__(*args, **kwargs)
        with cls._lock:
            if m.identity in metrics_mapping:
                return metrics_mapping[m.identity]
            else:
                m.init(manager)
                metrics_mapping[m.identity] = m
                return metrics_mapping[m.identity]

    @classmethod
    def collect(mcs) -> Iterator[Metric]:
        """Yields metrics from the collectors in the registry."""
        from derive.metrics.manager import metrics_mapping

        yield from metrics_mapping.values()
