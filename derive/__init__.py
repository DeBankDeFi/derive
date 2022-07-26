import os
import sys
import typing
from threading import Lock

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk import resources

from derive import log as logging
from derive import trace
from derive.config import DefaultConfig
from derive.config import DefaultConfig
from derive.integrations import BaseIntegration

_installer_lock = Lock()
_installed_integrations: typing.Set[str] = set()
_global_resources: Resource = Resource.create()


def update_global_resources(resource: Resource) -> None:
    global _global_resources
    _global_resources = _global_resources.merge(resource)


def get_global_resources() -> Resource:
    return _global_resources


def init(
    config: DefaultConfig,
    integrations: typing.Optional[typing.Iterable[BaseIntegration]] = None,
):
    update_global_resources(Resource({resources.SERVICE_NAME: config.SERVICE_NAME}))
    update_global_resources(Resource(config.STATIC_RESOURCES))
    with _installer_lock:
        for integration in integrations or []:
            if integration.identifier not in _installed_integrations:
                integration.setup()
                _installed_integrations.add(integration.identifier)


def register_after_fork(f: typing.Callable[..., typing.Any]) -> None:
    try:
        import uwsgidecorators
    except ImportError:
        pass
    else:
        uwsgidecorators.postfork(f)
    if not sys.platform.startswith("win"):
        os.register_at_fork(after_in_child=f)
