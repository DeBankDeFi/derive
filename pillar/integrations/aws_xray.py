from configalchemy import BaseConfig
from pillar.trace import set_tracer
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.sdk.trace.sampling import (
    ParentBasedTraceIdRatio,
    ParentBased,
    ALWAYS_ON,
)

from pillar.integrations import BaseIntegration


class DefaultConfig(BaseConfig):
    ENABLE = False
    OTLP_ENDPOINT = ""
    SAMPLING_RATE = 0.1


class Integration(BaseIntegration):
    @property
    def identifier(self) -> str:
        return "aws-xray"

    def __init__(self, config: DefaultConfig) -> None:
        self.config = config

    def setup_trace(self):
        if self.config.ENABLE:
            otlp_exporter = OTLPSpanExporter(endpoint=self.config.OTLP_ENDPOINT)
            span_processor = BatchSpanProcessor(otlp_exporter)
            if self.config.SAMPLING_RATE == 1.0:
                sampler = ParentBased(ALWAYS_ON)
            else:
                sampler = ParentBasedTraceIdRatio(self.config.SAMPLING_RATE)
            tracer_provider = TracerProvider(
                sampler=sampler, id_generator=AwsXRayIdGenerator()
            )
            tracer_provider.add_span_processor(span_processor)
            set_tracer(tracer_provider.get_tracer("aws-xray"))
