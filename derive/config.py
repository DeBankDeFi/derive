from configalchemy import BaseConfig
from opentelemetry.sdk.resources import Attributes


class DefaultConfig(BaseConfig):
    SERVICE_NAME = "derive"

    STATIC_RESOURCES: Attributes = {}
