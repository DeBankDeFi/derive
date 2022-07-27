from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from derive import trace
from derive.integrations import BaseIntegration


class Integration(BaseIntegration):
    @property
    def identifier(self) -> str:
        return "console"

    def setup(self):
        provider = TracerProvider()
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_provider(provider)
