from derive.metrics.collector import GlobalCollector
import typing

CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"


class Exporter:
    @classmethod
    def generate_latest(cls) -> str:
        pass


class PrometheusExporter(Exporter):
    @classmethod
    def generate_latest(cls) -> str:
        output: typing.List[str] = []
        for metric in GlobalCollector.collect():
            output.extend(metric.export())

        return "\n".join(output)
