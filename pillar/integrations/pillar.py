import typing

from opentelemetry.sdk import resources
from opentelemetry.sdk.trace import Resource

from pillar import trace
from pillar.config import DefaultConfig
from pillar.integrations import BaseIntegration


class Integration(BaseIntegration):
    @property
    def identifier(self) -> str:
        return "pillar"

    def __init__(self, config: DefaultConfig):
        self.config = config

    def setup_trace(self):
        tracer = trace.get_tracer()
        resource: typing.Optional[resources.Resource] = getattr(
            tracer, "resource", Resource.create({})
        )
        attributes: resources.Attributes = {
            resources.SERVICE_NAME: self.config.PILLAR_SERVICE_NAME
        }
        setattr(tracer, "resource", resource.merge(Resource(attributes=attributes)))
