import typing
from threading import Lock

from pillar.config import DefaultConfig
from pillar.integrations import BaseIntegration, pillar
from itertools import chain

_installer_lock = Lock()
_installed_integrations: typing.Set[str] = set()


def init(
    config: DefaultConfig,
    integrations: typing.Optional[typing.Iterable[BaseIntegration]] = None,
):
    with _installer_lock:
        for integration in chain([pillar.Integration(config)], integrations or []):
            if integration.identifier not in _installed_integrations:
                integration.setup()
                _installed_integrations.add(integration.identifier)
