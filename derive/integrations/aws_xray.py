import typing

from configalchemy import BaseConfig
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.aws import AwsXRayPropagator
from opentelemetry.sdk import resources
from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator
from opentelemetry.sdk.trace import TracerProvider, SynchronousMultiSpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import (
    ParentBasedTraceIdRatio,
    ParentBased,
    ALWAYS_ON,
)

import derive
from derive import trace
from derive.integrations import BaseIntegration


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
            origin_tracer = trace.get_tracer()
            resource: typing.Optional[resources.Resource] = getattr(
                origin_tracer, "resource", resources.Resource.create({})
            )
            resource = resource.merge(derive.get_global_resources())
            tracer_provider = TracerProvider(
                sampler=sampler,
                resource=resource,
                id_generator=AwsXRayIdGenerator(),
                active_span_processor=typing.cast(
                    SynchronousMultiSpanProcessor, span_processor
                ),
            )
            trace.set_provider(tracer_provider)
            set_global_textmap(AwsXRayPropagator())
