import os
import sys
import typing
from threading import Lock

from pillar import log as logging
from pillar import trace
from pillar.config import DefaultConfig
from pillar.config import DefaultConfig
from pillar.integrations import BaseIntegration

_installer_lock = Lock()
_installed_integrations: typing.Set[str] = set()


def init(
    config: DefaultConfig,
    integrations: typing.Optional[typing.Iterable[BaseIntegration]] = None,
):
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
