import typing

from configalchemy import BaseConfig


class DefaultConfig(BaseConfig):
    SERVICE_NAME = "pillar"

    STATIC_RESOURCES: typing.Mapping[str, str] = {}
