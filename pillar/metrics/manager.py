from __future__ import annotations

import os
import sys
from multiprocessing import Manager, process, set_start_method
from multiprocessing.managers import SyncManager
from typing import MutableMapping

from pillar.metrics.metric.base import Metric, MetricValue, MetricValueProxy

if sys.platform == "darwin":
    set_start_method("fork", force=True)

SyncManager.register("MetricValue", MetricValue, MetricValueProxy)
manager = Manager()
metrics_mapping: MutableMapping[str, Metric] = manager.dict()


def _reset_children():
    """Reset children in child after fork to avoid exception in multiprocessing.util._exit_function upon normal program termination.
    Same implement in multiprocessing.process.BaseProcess._bootstrap"""
    process._children = set()


try:
    import uwsgidecorators
except ImportError:
    pass
else:
    uwsgidecorators.postfork(_reset_children)

if not sys.platform.startswith("win"):
    os.register_at_fork(after_in_child=_reset_children)