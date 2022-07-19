from pillar.integrations import BaseIntegration
from pillar.integrations import DidNotEnable

try:
    import requests
except ImportError:
    raise DidNotEnable("requests is not installed")
from opentelemetry.instrumentation.requests import RequestsInstrumentor


class Integration(BaseIntegration):
    @property
    def identifier(self) -> str:
        return "requests"

    def setup_trace(self):
        RequestsInstrumentor().instrument()
