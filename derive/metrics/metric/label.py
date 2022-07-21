from typing import Tuple, TypeVar, Generic, Type, Set

from derive.metrics.metric import base

M = TypeVar("M", bound=base.Metric)


class _MetricMeta(type):
    def __new__(cls, cls_name: str, bases: Tuple, cls_dict: dict):
        _cls = super().__new__(cls, cls_name, bases, cls_dict)
        setattr(_cls, "m_cls", getattr(_cls, "__orig_bases__")[0].__args__[0])
        return _cls


class _Metric(Generic[M], metaclass=_MetricMeta):
    m_cls: Type[M]

    def __init__(self, name: str, document: str, label_names: Set[str]):
        self.label_names = label_names
        self.parameters = dict(name=name, document=document)

    def labels(self, **kwargs: str) -> M:
        """
        All metrics can have labels, allowing grouping of related time series.
        Taking a counter as an example:

            from derive.metrics import Counter

            c = Counter('my_requests_total', 'HTTP Failures', {"method","endpoint"})
            c.labels(method="get", endpoint="/").inc()
            c.labels(method='post', endpoint='/submit').inc()
        """
        if self.label_names != kwargs.keys():
            raise ValueError("Incorrect label names")
        return self.m_cls(**self.parameters, labels=kwargs)


class Counter(_Metric[base.Counter]):
    pass


class Gauge(_Metric[base.Gauge]):
    pass


class Summary(_Metric[base.Summary]):
    pass


class Histogram(_Metric[base.Histogram]):
    def __init__(self, *args, buckets=base.Histogram.DEFAULT_BUCKETS, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters.update(buckets=buckets)
